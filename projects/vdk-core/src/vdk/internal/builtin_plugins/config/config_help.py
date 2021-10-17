# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import re
from collections import OrderedDict
from textwrap import wrap
from typing import cast

import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.core.context import CoreContext

log = logging.getLogger(__name__)

CONFIG_HELP = """
Configuring VDK is done via:
{config_providers}
-----------

List of configuration variables:
{config_variables}

------------

How to set them?\n
The above listed configuration variables can be set using following configuration providers:\n
{config_providers}
"""


def description_line_wrapping(description, description_start=40, description_length=60):
    wrapped_text_list = []
    description_paragraphs = description.splitlines()
    for paragraph in description_paragraphs:
        wrapped_text_list += wrap(
            paragraph,
            width=description_length,
            break_long_words=False,
            break_on_hyphens=False,
        )
    indent = " " * description_start
    # we do not need to wrap the first line (it's already padded to the config key)
    for index, line in enumerate(wrapped_text_list[1:], start=1):
        wrapped_text_list[index] = indent + wrapped_text_list[index]
    return "\n".join(wrapped_text_list)


def description_cleanup(config_variable: str, description: str, description_start: int):
    if description:
        description = re.sub(" +", " ", description)
        description = re.sub("\n ", "\n", description)
        description = description.strip()
        if len(config_variable) > description_start:
            description = "  " + description
    return description


# Description length can be configured by changing the default value for description_length
def formatted_configuration_help(
    config_variable, description, description_start=40, description_length=60
):
    config_variable = config_variable.strip()
    padding = " " * (description_start - len(config_variable))
    conf_help = "{config_var}{padding}{description}"
    description = description_cleanup(config_variable, description, description_start)
    return conf_help.format(
        config_var=config_variable,
        padding=padding,
        description=description_line_wrapping(
            description, description_start, description_length
        ),
    )


def generate_config_list_help(variable_to_description_map):
    config_list = "\n\n"
    conf_variable_list = []
    for key in variable_to_description_map:
        conf_variable_list.append(
            formatted_configuration_help(key, variable_to_description_map[key])
        )
    return config_list.join(conf_variable_list)


@click.command(
    help="Print details on configuration options of vdk. "
    "It includes all configuration options added by plugins."
    """

Examples:

\b
# if we call config-help we get similar output to one below.
# first we provide details on how those configuration can be set (e.g environment variables, files, etc)
# Next list of all possible configuration variables supported.
vdk config-help

\b
Configuring VDK is done via:
environment variables                   Attempts to load all defined configurations using
                                        environment variables by adding prefix "VDK_".
                                        ...
-----
List of configuration variables:
DB_DEFAULT_TYPE                         Default DB connection provided by VDK when ..
EXECUTION_ID                            An identifier to be associated with the current VDK run ...
    """
)
@click.pass_context
def config_help(ctx: click.Context) -> None:
    configuration = cast(CoreContext, ctx.obj).configuration

    vars_to_descriptions = {}
    providers_descriptions = {}
    for k in configuration.list_config_keys():
        description = configuration.get_description(k)
        if description:
            if k.startswith("__config_provider__"):
                name = k[len("__config_provider__") :].strip()
                providers_descriptions[name] = description
            else:
                vars_to_descriptions[k] = description

    click.echo(
        CONFIG_HELP.format(
            config_providers=generate_config_list_help(
                OrderedDict(sorted(providers_descriptions.items()))
            ),
            config_variables=generate_config_list_help(
                OrderedDict(sorted(vars_to_descriptions.items()))
            ),
        )
    )


class ConfigHelpPlugin:
    """
    The following plugins add a new command (vdk conflig-help) which would enable
    users to query for possible configurations. Each plugin declare their possible configuration
    in vdk_configure hook (using config_builder.add) providng descriptions and other attributes,
    Those then can be queried by end users. See vdk_configure doc for more information.
    """

    @hookimpl
    def vdk_command_line(self, root_command: click.Group) -> None:
        """
        Modify command line arguments to add config help option
        """
        root_command.add_command(config_help)
