from typing import List
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry


from vdk.internal.core.context import CoreContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.confluence_data_source.data_source import ConfluenceDataSourceDataSource


class DataSourcePlugin:

    @hookimpl
    def vdk_data_sources_register(self,
                                  data_source_factory: IDataSourceFactory):
        data_source_factory.register_data_source_class(ConfluenceDataSourceDataSource)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(DataSourcePlugin(), "DataSourceConfluenceDataSource")



