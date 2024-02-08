# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Iterator
from typing import List
from typing import Optional

from atlassian import Confluence
from dateutil import parser
from retrying import retry
from vdk.plugin.data_sources.config import config_class
from vdk.plugin.data_sources.config import config_field
from vdk.plugin.data_sources.data_source import DataSourcePayload
from vdk.plugin.data_sources.data_source import IDataSource
from vdk.plugin.data_sources.data_source import IDataSourceConfiguration
from vdk.plugin.data_sources.data_source import IDataSourceStream
from vdk.plugin.data_sources.factory import data_source


@config_class(
    name="confluence-page-content", description="Stream Confluence page contents"
)
class ConfluenceContentDataSourceConfiguration(IDataSourceConfiguration):
    confluence_url: str = config_field(description="URL of the Confluence site")
    space_key: str = config_field(description="Key of the Confluence space")
    username: Optional[str] = config_field(
        description="Confluence username for authentication", default=None
    )
    api_token: Optional[str] = config_field(
        description="Confluence API token for authentication", default=None
    )
    personal_access_token: Optional[str] = config_field(
        description="Confluence personal access token for" " authentication",
        default=None,
    )
    oauth2: Optional[dict] = config_field(
        description="OAuth2 credentials for authentication "
        "in dictionary format. Required keys: 'access_token',"
        " 'access_token_secret', 'consumer_key', 'key_cert'",
        default=None,
    )
    cloud: bool = config_field(
        description="Flag indicating if the Confluence instance is" " cloud-based",
        default=True,
    )
    confluence_kwargs: Optional[dict] = config_field(
        description="Additional keyword arguments " "for the Confluence client",
        default=None,
    )


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
            self._streams.append(
                PageContentStream(
                    url=self._config.confluence_url,
                    space_key=self._config.space_key,
                    username=self._config.username,
                    api_key=self._config.api_token,
                    token=self._config.personal_access_token,
                    oauth2=self._config.oauth2,
                    cloud=self._config.cloud,
                    confluence_kwargs=self._config.confluence_kwargs,
                )
            )

    def disconnect(self):
        self._streams = []

    def streams(self) -> List[IDataSourceStream]:
        return self._streams


class PageContentStream(IDataSourceStream):
    """
    A stream class for fetching content from Confluence pages within a specified space.

    This class initializes a connection to a Confluence instance and provides a method to read and stream content
    from pages. It supports multiple authentication methods including basic authentication with username and API key,
     OAuth2, and personal access tokens. The stream can optionally filter pages updated after a specified timestamp.

    Usage Example:
        # Basic authentication
        stream = PageContentStream(
            url="https://your-confluence-instance.atlassian.net/wiki",
            space_key="SPACE_KEY",
            username="user",
            api_key="secret"
        )

        # Using a personal access token
        stream = PageContentStream(
            url="https://your-confluence-instance.atlassian.net/wiki",
            space_key="SPACE_KEY",
            token="your_token"
        )

        # Iterating through page content
        for page in stream.read(last_check_timestamp="2022-02-14T01:42:29.000-08:00"):
            print(page.data, page.metadata)
    """

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

        auth_methods = [username, token, oauth2]
        if sum(bool(method) for method in auth_methods) > 1:
            raise ValueError("Only one authentication method should be provided")

        confluence_kwargs = confluence_kwargs or {}
        if oauth2:
            self.confluence = Confluence(
                url=url, oauth2=oauth2, cloud=cloud, **confluence_kwargs
            )
        elif token:
            self.confluence = Confluence(
                url=url, token=token, cloud=cloud, **confluence_kwargs
            )
        else:
            if not username or not api_key:
                raise ValueError(
                    "Username and API key are required for basic authentication"
                )
            self.confluence = Confluence(
                url=url,
                username=username,
                password=api_key,
                cloud=cloud,
                **confluence_kwargs,
            )

        self.space_key = space_key

    def name(self) -> str:
        return f"confluence-space-{self.space_key}-page-content"

    @retry(
        stop_max_attempt_number=3,
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
    )
    def read(
        self, last_check_timestamp: Optional[str] = None
    ) -> Iterator[DataSourcePayload]:
        limit = 50  # TODO: should be adjustable value as needed to comply with API limitations and user requirements
        start = 0
        more_pages = True

        while more_pages:
            try:
                pages = self.confluence.get_all_pages_from_space(
                    space=self.space_key,
                    start=start,
                    limit=limit,
                    expand="body.storage,version,history.lastUpdated",
                )
                if pages:
                    for page in pages:
                        last_updated_str = page["history"]["lastUpdated"]["when"]
                        last_updated = parser.isoparse(last_updated_str)

                        if last_check_timestamp:
                            last_check_dt = parser.isoparse(last_check_timestamp)
                            if last_updated <= last_check_dt:
                                continue

                        data = page["body"]["storage"]["value"]
                        metadata = {
                            "page_id": page["id"],
                            "space_key": self.space_key,
                            "title": page["title"],
                            "last_modified": last_updated_str,
                            "version": page["version"]["number"],
                            "status": "existing",
                        }
                        yield DataSourcePayload(data=data, metadata=metadata)
                    start += limit
                else:
                    more_pages = False
            except Exception as e:
                logging.error(f"Failed to fetch page updates: {e}")
                raise


# TODO: add stream for deletions
