# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.mapping.data_flow import DataFlowInput
from vdk.plugin.data_sources.mapping.definitions import DataFlowMappingDefinition
from vdk.plugin.data_sources.mapping.definitions import DestinationDefinition
from vdk.plugin.data_sources.mapping.definitions import SourceDefinition


def run(job_input: IJobInput):
    config = {
        "confluence_url": "https://your-confluence-instance.atlassian.net/wiki",
        "api_token": "token",
        "space_key": "SPACE_KEY",
        "cloud": True,
        "confluence_kwargs": {},
        "username": None,
        "personal_access_token": None,
        "oauth2": None,
    }
    source = SourceDefinition(id="pages", name="confluence", config=config)
    destination = DestinationDefinition(id="test", method="memory")

    with DataFlowInput(job_input) as flow_input:
        flow_input.start(DataFlowMappingDefinition(source, destination))
