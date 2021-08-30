# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from collections import OrderedDict
from textwrap import wrap
from typing import cast

import click
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.core.context import CoreContext

log = logging.getLogger(__name__)

CONFIG_HELP = """
Configuring VDK is done via:
{config_providers}
-----

List of configuration variables:
{config_variables}
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


# Description length can be configured by changing the default value for description_length
def formatted_configuration_help(
    config_variable, description, description_start=40, description_length=60
):
    config_variable = config_variable.strip()
    padding = " " * (description_start - len(config_variable))
    conf_help = "{config_var}{padding}{description}"
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
    help="Configuration help."
    "Prints details on all possible configuration options of vdk ."
    "It includes all configuration options added by plugins"
    """

Examples:

\b
# if we call config-help we get similar output to one below.
# first we provide details on how those configuration can be set (e.g environment varibales, files, etc)
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
    for k, v in configuration.config_key_to_description.items():
        if k.startswith("__config_provider__"):
            name = k[len("__config_provider__") :].strip()
            providers_descriptions[name] = v
        else:
            vars_to_descriptions[k] = v

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
