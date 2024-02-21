# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.plugin.singer.singer_command import singer
from vdk.plugin.singer.singer_data_source import SingerDataSource

"""
Entry point for singer plugins implementations.
"""


# TODO:
# It is very difficult ot install two or more different taps in teh same environment
# They almost certainly use conflicting libraries of singer-python and possibly others.
# This likely means we need a mechanism where those taps would be installed inseparate virtual environments
# possibility is to use pipx or similar tool as we treat singer taps as applications /CLIs and not libraries.
#
# An idea is to add `vdk build` and vkd_build hook in vdk-core.
# It will be called before vdk run (if not called) when running locally
# And it can be called by the Control Service Deployer to install taps in the job docker image.


@hookimpl
def vdk_data_sources_register(data_source_factory: "IDataSourceFactory"):
    data_source_factory.register_data_source_class(SingerDataSource)


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(singer)
