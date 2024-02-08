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
    """
        A data source class for streaming content from Confluence. This class is responsible for
        configuring and managing connections to a Confluence instance, and it provides methods to
        connect to, disconnect from, and retrieve streams of data from Confluence.

        The data source supports multiple authentication methods including basic authentication with
        username and API token, OAuth2, and personal access tokens. It initializes a single Confluence
        client based on the provided configuration and uses this client across different streams to
        fetch page content, comments, or other Confluence entities.

        Example:

            ```python
            config = ConfluenceContentDataSourceConfiguration(
                confluence_url="https://your-confluence-instance.atlassian.net/wiki",
                space_key="SPACE_KEY",
                username="user",
                api_token="secret"
            )
            confluence_data_source = ConfluenceDataSource()
            confluence_data_source.configure(config)
            confluence_data_source.connect(state=None)

            for stream in confluence_data_source.streams():
                for page_content in stream.read():
                    print(page_content.data, page_content.metadata)

            confluence_data_source.disconnect()
            ```

        """
    def __init__(self):
        self._config = None
        self._confluence_client = None
        self._streams = []

    def configure(self, config: ConfluenceContentDataSourceConfiguration):
        self._config = config
        self._initialize_confluence_client()

    def _initialize_confluence_client(self):
        """Initialize the Confluence client based on the provided configuration."""
        confluence_kwargs = self._config.confluence_kwargs or {}
        if self._config.oauth2:
            self._confluence_client = Confluence(
                url=self._config.confluence_url, oauth2=self._config.oauth2, cloud=self._config.cloud,
                **confluence_kwargs
            )
        elif self._config.api_token:
            self._confluence_client = Confluence(
                url=self._config.confluence_url, token=self._config.api_token, cloud=self._config.cloud,
                **confluence_kwargs
            )
        else:
            if not self._config.username or not self._config.personal_access_token:
                raise ValueError("Username and API token are required for basic authentication")
            self._confluence_client = Confluence(
                url=self._config.confluence_url,
                username=self._config.username,
                password=self._config.api_token,
                cloud=self._config.cloud,
                **confluence_kwargs,
            )

    def connect(self, state):
        if not self._streams and self._confluence_client:
            if self._config.space_key:
                # if a space_key is provided, create a stream for that space only
                self._streams.append(
                    PageContentStream(
                        confluence_client=self._confluence_client,
                        space_key=self._config.space_key,
                    )
                )
            else:
                # no space_key provided, fetch all accessible spaces and create a stream for each
                try:
                    spaces = self._confluence_client.get_all_spaces(limit=1000)  # we should adjust the limit as needed
                    for space in spaces:
                        space_key = space['key']
                        self._streams.append(
                            PageContentStream(
                                confluence_client=self._confluence_client,
                                space_key=space_key,
                            )
                        )
                except Exception as e:
                    logging.error(f"Failed to fetch spaces from Confluence: {e}")
                    raise

    def disconnect(self):
        self._streams = []

    def streams(self) -> List[IDataSourceStream]:
        return self._streams


class PageContentStream(IDataSourceStream):
    """
    A stream class for fetching content from Confluence pages within a specified space.

    Example:
        # Iterating through page content
        for page in stream.read(last_check_timestamp="2022-02-14T01:42:29.000-08:00"):
            print(page.data, page.metadata)
    """

    def __init__(
        self,
        confluence_client: Confluence,
        space_key: str,
    ):
        self.confluence = confluence_client
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
