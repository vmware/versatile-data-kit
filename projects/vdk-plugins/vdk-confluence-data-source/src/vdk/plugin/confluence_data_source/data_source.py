import logging
from dateutil import parser
from typing import List, Iterator, Optional
from atlassian import Confluence
from retrying import retry
from vdk.plugin.data_sources.data_source import IDataSourceConfiguration, IDataSource, IDataSourceStream, \
    DataSourcePayload
from vdk.plugin.data_sources.config import config_class, config_field
from vdk.plugin.data_sources.factory import data_source


@config_class(name="confluence-page-content", description="Stream Confluence page contents")
class ConfluenceContentDataSourceConfiguration(IDataSourceConfiguration):
    confluence_url: str = config_field(description="URL of the Confluence site")
    username: str = config_field(description="Confluence username for authentication")
    api_token: str = config_field(description="Confluence API token for authentication")
    space_key: str = config_field(description="Key of the Confluence space")


@data_source(
    name="confluence-content", config_class=ConfluenceContentDataSourceConfiguration
)
class ConfluenceDataSource(IDataSource):
    def __init__(self):
        self._config = None
        self._streams = []

    def configure(self, config: ConfluenceContentDataSourceConfiguration):
        self._config = config

    def connect(self, state):
        if not self._streams:
            self._streams.append(PageContentStream(
                self._config.confluence_url,
                self._config.username,
                self._config.api_token,
                self._config.space_key
            ))

    def disconnect(self):
        self._streams = []

    def streams(self) -> List[IDataSourceStream]:
        return self._streams


class PageContentStream(IDataSourceStream):
    def __init__(
            self,
            url: str,
            space_key: str,
            username: Optional[str] = None,
            api_key: Optional[str] = None,
            token: Optional[str] = None,
            oauth2: Optional[dict] = None,
            cloud: bool = True,
            confluence_kwargs: Optional[dict] = None,
    ):
        if not url:
            raise ValueError("URL is required")
        if not space_key:
            raise ValueError("Space key is required")

        auth_methods = [username, api_key, token, oauth2]
        if sum(bool(method) for method in auth_methods) > 1:
            raise ValueError("Only one authentication method should be provided")

        confluence_kwargs = confluence_kwargs or {}
        if oauth2:
            self.confluence = Confluence(url=url, oauth2=oauth2, cloud=cloud, **confluence_kwargs)
        elif token:
            self.confluence = Confluence(url=url, token=token, cloud=cloud, **confluence_kwargs)
        else:
            if not username or not api_key:
                raise ValueError("Username and API key are required for basic authentication")
            self.confluence = Confluence(url=url, username=username, password=api_key, cloud=cloud, **confluence_kwargs)

        self.space_key = space_key

    def name(self) -> str:
        return f"confluence-space-{self.space_key}-page-content"

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def read(self, last_check_timestamp: Optional[str] = None) -> Iterator[DataSourcePayload]:
        limit = 50
        start = 0
        more_pages = True

        while more_pages:
            try:
                pages = self.confluence.get_all_pages_from_space(space=self.space_key, start=start, limit=limit,
                                                                 expand="body.storage,version,history.lastUpdated")
                if pages:
                    for page in pages:
                        last_updated_str = page['history']['lastUpdated']['when']
                        last_updated = parser.isoparse(last_updated_str)

                        if last_check_timestamp:
                            last_check_dt = parser.isoparse(last_check_timestamp)
                            if last_updated <= last_check_dt:
                                continue

                        data = page['body']['storage']['value']
                        metadata = {
                            "page_id": page['id'],
                            "space_key": self.space_key,
                            "title": page['title'],
                            "last_modified": last_updated_str,
                            "version": page['version']['number'],
                            "status": "existing"
                        }
                        yield DataSourcePayload(data=data, metadata=metadata)
                    start += limit
                else:
                    more_pages = False
            except Exception as e:
                logging.error(f"Failed to fetch page updates: {e}")
                raise


# TODO: add stream for deletions


