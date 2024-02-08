# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import logging

from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.mapping.data_flow import DataFlowInput
from vdk.plugin.data_sources.mapping.definitions import DataFlowMappingDefinition
from vdk.plugin.data_sources.mapping.definitions import DestinationDefinition
from vdk.plugin.data_sources.mapping.definitions import SourceDefinition

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    source = SourceDefinition(
        id="test-data-source",
        name="confluence-data-source",
        config=job_input.get_arguments("config", {}),
    )
    destination = DestinationDefinition(id="test-destination", method="memory")

    with DataFlowInput(job_input) as flow_input:
        flow_input.start(DataFlowMappingDefinition(source, destination))
