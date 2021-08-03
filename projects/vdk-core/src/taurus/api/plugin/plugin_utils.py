# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict

import click
from taurus.vdk.core import errors

log = logging.getLogger(__name__)


def set_defaults_for_specific_command(
    root_command: click.Group, target_command: str, defaults_dict: Dict[str, str]
) -> None:
    """
    Function which specifies default values for parameters of the target_command subcommand in root_command

    :param root_command: root command which contains all subcommands
    :param target_command: the name of the command whose defaults we want to specify in string form
    :param defaults_dict: a key-value store where keys are the names of parameters, values are the new default values
    """
    if not isinstance(root_command, click.Group):
        errors.log_and_throw(
            to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
            log=log,
            what_happened=f"Cannot set default parameters when root_command isn't of type click.Group",
            why_it_happened=f"A plugin which attempted to set default parameters was not given a root_command object of type click.Group",
            consequences="Cannot continue with execution",
            countermeasures=f"Fix or uninstall buggy plugin",
        )
    if len(defaults_dict) == 0:
        log.debug("defaults_dict is empty, please provide default parameter values")

    command = root_command.get_command(None, target_command)
    if command is None:
        errors.log_and_throw(
            to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
            log=log,
            what_happened=f"Cannot set default parameters for non-existing command: {target_command}",
            why_it_happened=f"A plugin attempted to set default parameters for non-existing command: {target_command}",
            consequences="Cannot continue with execution",
            countermeasures=f"Fix or uninstall plugin which sets command: {target_command}",
        )
    for param in command.params:
        if param.name in defaults_dict.keys():
            param.default = defaults_dict.pop(param.name)

    if len(defaults_dict) > 0:
        log.debug(
            "Did not find the following parameters: ", set(defaults_dict.keys())
        )  # TODO: maybe raise an exception?


def set_defaults_for_all_commands(
    root_command: click.Group, defaults_dict: Dict[str, str]
) -> None:
    """
    Function which specifies default values for parameters of all subcommands in root_command

    :param root_command: root command which contains all subcommands
    :param defaults_dict: a key-value store where keys are the names of parameters, values are the new default values
    """
    if not isinstance(root_command, click.Group):
        errors.log_and_throw(
            to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
            log=log,
            what_happened=f"Cannot set default parameters when root_command isn't of type click.Group",
            why_it_happened=f"A plugin which attempted to set default parameters was not given a root_command object of type click.Group",
            consequences="Cannot continue with execution",
            countermeasures=f"Fix or uninstall buggy plugin",
        )
    if len(defaults_dict) == 0:
        log.debug("defaults_dict is empty, please provide default parameter values")

    params_to_be_specified = set(defaults_dict.keys())
    discovered_params = set()
    for command_name in root_command.list_commands(None):
        command = root_command.get_command(None, command_name)
        for param in command.params:
            if param.name in defaults_dict.keys():
                param.default = defaults_dict[param.name]
                discovered_params.add(param.name)

    if discovered_params != params_to_be_specified:
        log.debug(
            "Did not find the following parameters: ",
            params_to_be_specified.difference(discovered_params),
        )
