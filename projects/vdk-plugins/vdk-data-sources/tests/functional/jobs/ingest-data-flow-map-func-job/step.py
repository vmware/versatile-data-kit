# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.data_source import DataSourcePayload
from vdk.plugin.data_sources.mapping.data_flow import DataFlowInput
from vdk.plugin.data_sources.mapping.definitions import DataFlowMappingDefinition
from vdk.plugin.data_sources.mapping.definitions import DestinationDefinition
from vdk.plugin.data_sources.mapping.definitions import SourceDefinition


def run(job_input: IJobInput):
    source = SourceDefinition(id="auto", name="auto-generated-data", config={})
    destination = DestinationDefinition(id="auto-dest", method="memory")

    def map_func(p: DataSourcePayload):
        p.data["new_column"] = "new_column"
        return p

    with DataFlowInput(job_input) as flow_input:
        flow_input.start(DataFlowMappingDefinition(source, destination, map_func))
