# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.factory import SingletonDataSourceFactory
from vdk.plugin.data_sources.ingester import DataSourceIngester
from vdk.plugin.data_sources.ingester import IngestDestination
from vdk.plugin.data_sources.mapping.definitions import DataFlowMappingDefinition
from vdk.plugin.data_sources.mapping.definitions import Definitions


class DataFlowInput:
    """
    Manages the data flow from source to destination using the provided job input.

    :param job_input: Instance of IJobInput, providing context for the current job.
    """

    def __init__(self, job_input: IJobInput):
        self._job_input = job_input
        self._data_source_ingester = DataSourceIngester(job_input)
        self._data_source_factory = SingletonDataSourceFactory()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Terminates and waits for data source ingestion to finish.
        """
        self._data_source_ingester.terminate_and_wait_to_finish()
        self._data_source_ingester.raise_on_error()

    def start(self, flow_definition: DataFlowMappingDefinition):
        """
        Start data flow from a specific source to a specific destination.

        :param flow_definition: The definition of the source and destination flow.
        """
        source = self._data_source_factory.create_data_source(
            flow_definition.from_source.name
        )
        source_config = self._data_source_factory.create_configuration(
            flow_definition.from_source.name, flow_definition.from_source.config
        )
        source.configure(source_config)

        destination = IngestDestination(
            method=flow_definition.to_destination.method,
            target=flow_definition.to_destination.target,
            map_function=flow_definition.map_function,
        )
        self._data_source_ingester.start_ingestion(
            flow_definition.from_source.id, source, [destination]
        )

    def start_flows(self, definitions: Definitions):
        """
        Start data flows based on a list of defined mappings.

        :param definitions: Definitions containing the data flow mappings.
        """
        for flowDefinition in definitions.flows:
            self.start(flowDefinition)
