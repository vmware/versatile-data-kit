# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from typing import Dict
from typing import List

import click
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils import output_printer
from vdk.plugin.data_sources.config import ConfigClassMetadata
from vdk.plugin.data_sources.factory import SingletonDataSourceFactory


def list_data_sources() -> List[Dict]:
    result = []
    for source in SingletonDataSourceFactory().list():
        item = {
            "name": source.name,
            "description": ConfigClassMetadata(source.config_class).get_description(),
        }

        result.append(item)
    return result


def list_config_options(data_source_name: str) -> List[Dict]:
    result = []
    sources = [
        s for s in SingletonDataSourceFactory().list() if s.name == data_source_name
    ]
    if sources:
        source = sources[0]
        for field in ConfigClassMetadata(source.config_class).get_config_fields():
            result.append(
                dict(
                    name=field.name(),
                    description=field.description()
                    + (
                        f" (default: {field.default()})"
                        if field.default() is not None
                        else ""
                    ),
                )
            )
    return result


# TODO using ConfigClassMetadata fields you can create prompt to automatically ask config options
# and generate data flow file out of that. `vdk sources --interactive`


@click.command(
    name="data-sources",
    help="Explore VDK data sources ."
    """This command all registered data sources

     Example:
     # To list all data sources, run:
     `vdk data-sources --list`

     # To show config options for give data source
     vdk data-sources --config csv
     """,
)
@click.option(
    "--list", is_flag=True, help="List registered data sources that can be used. "
)
@click.option(
    "--config",
    type=click.STRING,
    help="List configuration options for the data source ",
)
@click.pass_context
@cli_utils.output_option()
def data_sources(ctx: click.Context, list: bool, config: str, output: str):
    if list:
        listed_sources = list_data_sources()
        output_printer.create_printer(output).print_table(listed_sources)
    if config:
        output_printer.create_printer(output).print_table(list_config_options(config))
