# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.factory import SingletonDataSourceFactory
from vdk.plugin.data_sources.ingester import DataSourceIngester
from vdk.plugin.data_sources.ingester import IngestDestination
from vdk.plugin.data_sources.mapping.definitions import Definitions
from vdk.plugin.data_sources.mapping.definitions import DestinationDefinition
from vdk.plugin.data_sources.mapping.definitions import SourceDefinition


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

    def start(
        self,
        source_definition: SourceDefinition,
        destination_definition: DestinationDefinition,
    ):
        """
        Start data flow from a specific source to a specific destination.

        :param source_definition: The definition of the source.
        :param destination_definition: The definition of the destination.
        """
        source = self._data_source_factory.create_data_source(source_definition.name)
        source_config = self._data_source_factory.create_configuration(
            source_definition.name, source_definition.config
        )
        source.configure(source_config)

        destination = IngestDestination(
            method=destination_definition.method, target=destination_definition.target
        )
        self._data_source_ingester.start_ingestion(
            source_definition.id, source, [destination]
        )

    def start_flow(self, definitions: Definitions):
        """
        Start data flows based on a list of defined mappings.

        :param definitions: Definitions containing the data flow mappings.
        """
        for d in definitions.flows:
            self.start(d.from_source, d.to_destination)
