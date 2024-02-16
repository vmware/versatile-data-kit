# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.plugin.hook_markers import hookspec
from vdk.plugin.data_sources.factory import IDataSourceFactory


class DataSourcesHookSpec:
    @hookspec(historic=True)
    def vdk_data_sources_register(self, data_source_factory: IDataSourceFactory):
        """
        Register a data source and its associated configuration class.

        :param data_source_factory: the factory where the data sources should be registered. Provide those param:
            :name: The name identifier for the data source
            :data_source_class: The data source class that implements `IDataSource`. Only the type. Not an instance of it!

        Example::

            data_source_factory.register_data_source_class(data_source_class=CsvDataSource)

            #where CsvDataSource is like
            @data_source(name="csv", config_class=CsvDataSourceConfig)
            CsvDataSource(IDataSource):
               ...
        """
