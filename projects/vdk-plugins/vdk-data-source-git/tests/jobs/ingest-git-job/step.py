# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.mapping.data_flow import DataFlowInput
from vdk.plugin.data_sources.mapping.definitions import DataFlowMappingDefinition
from vdk.plugin.data_sources.mapping.definitions import DestinationDefinition
from vdk.plugin.data_sources.mapping.definitions import SourceDefinition


def run(job_input: IJobInput):
    url = "https://github.com/versatile-data-kit-demo/dsc"
    source = SourceDefinition(id=url, name="git", config={"git_url": url})
    destination = DestinationDefinition(id="test", method="memory")

    with DataFlowInput(job_input) as flow_input:
        flow_input.start(DataFlowMappingDefinition(source, destination))
