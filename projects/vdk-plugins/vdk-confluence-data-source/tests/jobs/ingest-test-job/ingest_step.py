# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os

from vdk.api.job_input import IJobInput
from vdk.plugin.confluence_data_source.data_source import ConfluenceDataSource
from vdk.plugin.data_sources.mapping.data_flow import DataFlowInput
from vdk.plugin.data_sources.mapping.definitions import DataFlowMappingDefinition
from vdk.plugin.data_sources.mapping.definitions import DestinationDefinition
from vdk.plugin.data_sources.mapping.definitions import SourceDefinition

log = logging.getLogger(__name__)


class ConfluenceContentDataSourceConfiguration:
    def __init__(self):
        self.confluence_url = os.getenv("CONFLUENCE_URL")
        self.api_token = os.getenv("CONFLUENCE_API_TOKEN")
        self.space_key = os.getenv("CONFLUENCE_SPACE_KEY", None)
        self.cloud = True
        self.confluence_kwargs = {}
        self.username = None
        self.personal_access_token = None
        self.oauth2 = None


def run():
    config = ConfluenceContentDataSourceConfiguration()

    confluence_data_source = ConfluenceDataSource()
    confluence_data_source.configure(config)

    confluence_data_source.connect(None)

    for stream in confluence_data_source.streams():
        for page_content in stream.read():
            print(page_content.data, page_content.metadata)

    confluence_data_source.disconnect()


run()
