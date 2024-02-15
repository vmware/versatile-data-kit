# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.data_sources.auto_generated import AutoGeneratedDataSource
from vdk.plugin.data_sources.config import ConfigClassMetadata
from vdk.plugin.data_sources.factory import IDataSourceFactory
from vdk.plugin.data_sources.factory import SingletonDataSourceFactory
from vdk.plugin.data_sources.hook_spec import DataSourcesHookSpec

"""
Include the plugins implementation. For example:
"""


class DataSourcesPlugin:
    @hookimpl
    def vdk_data_sources_register(self, data_source_factory: IDataSourceFactory):
        data_source_factory.register_data_source_class(AutoGeneratedDataSource)

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        # define the config options so they show up in the help.
        for ds in SingletonDataSourceFactory().list():
            config_class_meta = ConfigClassMetadata(ds.config_class)
            for field in config_class_meta.get_config_fields():
                group_name = config_class_meta.get_group_name()
                config_builder.add(
                    key=f"a data source {group_name} config's option {field.name()}",
                    default_value=field.default(),
                    description=field.description(),
                    is_sensitive=field.is_sensitive(),
                )


# TODO: add ingest.toml type of job step which would automatically execute ingestion flows declared in TOML wihtout any python code


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.add_hook_specs(DataSourcesHookSpec)
    plugin_registry.load_plugin_with_hooks_impl(
        DataSourcesPlugin(), "DataSourcesPlugin"
    )

    plugin_registry.hook().vdk_data_sources_register.call_historic(
        kwargs=dict(data_source_factory=SingletonDataSourceFactory())
    )


@hookimpl
def vdk_command_line(root_command: click.Group):
    from vdk.plugin.data_sources.sources_command import data_sources

    root_command.add_command(data_sources)
