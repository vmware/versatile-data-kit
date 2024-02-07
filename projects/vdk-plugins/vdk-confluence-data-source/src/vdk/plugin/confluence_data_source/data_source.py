import logging
from typing import List, Iterator, Optional
from atlassian import Confluence
from retrying import retry
from vdk.plugin.data_sources.data_source import IDataSourceConfiguration, IDataSource, IDataSourceStream, \
    DataSourcePayload
from vdk.plugin.data_sources.config import config_class, config_field
from vdk.plugin.data_sources.factory import data_source


@config_class(name="confluence-page-content", description="Stream Confluence page contents")
class PageContentDataSourceConfiguration(IDataSourceConfiguration):
    confluence_url: str = config_field(description="URL of the Confluence site")
    username: str = config_field(description="Confluence username for authentication")
    api_token: str = config_field(description="Confluence API token for authentication")
    space_key: str = config_field(description="Key of the Confluence space")


@data_source(
    name="confluence-page-content", config_class=PageContentDataSourceConfiguration
)
class ConfluenceDataSource(IDataSource):
    def __init__(self):
        self._config = None
        self._streams = []

    def configure(self, config: PageContentDataSourceConfiguration):
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
    def __init__(self, url: str, username: str, token: str, space_key: str):
        self.confluence = Confluence(url=url, username=username, password=token)
        self.space_key = space_key

    def name(self) -> str:
        return f"confluence-space-{self.space_key}-page-content"

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def read(self) -> Iterator[DataSourcePayload]:
        limit = 50
        start = 0
        more_pages = True

        while more_pages:
            try:
                pages = self.confluence.get_all_pages_from_space(space=self.space_key, start=start, limit=limit,
                                                                 expand="body.storage,version,history.lastUpdated")
                if pages:
                    for page in pages:
                        data = page['body']['storage']['value']
                        metadata = {
                            "page_id": page['id'],
                            "space_key": self.space_key,
                            "title": page['title'],
                            "last_modified": page['history']['lastUpdated']['when'],
                            "version": page['version']['number'],
                            "status": "existing"
                        }
                        yield DataSourcePayload(data=data, metadata=metadata)
                    start += limit
                else:
                    more_pages = False
            except Exception as e:
                logging.error(f"Failed to fetch pages: {e}")
                raise


class PageUpdatesStream(IDataSourceStream):
    def __init__(self, url: str, username: str, token: str, space_key: str):
        self.confluence = Confluence(url=url, username=username, password=token)
        self.space_key = space_key

    def name(self) -> str:
        return f"confluence-space-{self.space_key}-page-updates"

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
                        last_updated = page['history']['lastUpdated']['when']
                        # convert last_updated and last_check_timestamp to the same format if not already
                        if last_check_timestamp is None or last_updated > last_check_timestamp:
                            data = page['body']['storage']['value']
                            metadata = {
                                "page_id": page['id'],
                                "space_key": self.space_key,
                                "title": page['title'],
                                "last_modified": last_updated,
                                "version": page['version']['number'],
                                "status": "existing"  # assuming all pages loaded are existing; adjust as needed
                            }
                            yield DataSourcePayload(data=data, metadata=metadata)
                    start += limit
                else:
                    more_pages = False
            except Exception as e:
                logging.error(f"Failed to fetch page updates: {e}")
                raise


# TODO: add stream for deletions


