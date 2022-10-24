# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
import os
from logging import Logger
from typing import Any
from typing import List
from typing import Optional

from vdk.api.plugin.plugin_registry import PluginException
from vdk.internal.builtin_plugins.config.vdk_config import LOG_CONFIG
from vdk.internal.builtin_plugins.termination_message.writer import (
    TerminationMessageWriterPlugin,
)
from vdk.internal.builtin_plugins.termination_message.writer_configuration import (
    add_definitions,
)
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import ResolvableBy


def class_fqname(py_object: Any) -> str:
    """
    :param py_object: Any python object
    :return: the full qualified name of the class (package.package.classname)
    """
    module = inspect.getmodule(py_object)
    if module is None:
        return py_object.__class__.__name__
    return f"{py_object.__class__.__module__}.{py_object.__class__.__name__}"


def parse_config_sequence(
    cfg: Configuration, key: str, sep: Optional[str] = None
) -> List:
    """
    Parse a configuration variable, whose value is a string sequence, by a
    specified delimiter.
    :param cfg: Configuration
        The configuration of Versatile Data Kit.
    :param key: string
        The name of the configuration variable that is to be parsed.
    :param sep: string
        Optional. The delimiter by which the configuration variable string is
        to be split. If not specified or set as None, any whitespace will be
        considered a delimiter, and the result from the split will have no
        empty strings.
    :return:
    """
    sequence = cfg.get_value(key)
    if sequence:
        sequence = [i.strip() for i in sequence.split(sep)]
    return sequence if sequence else []


def exit_with_error(
    user_error: ResolvableBy, log: Logger, exception: Exception, group_name
):
    """
    Write a termination message, log and exit with specified error.
    Intended for use in cases when hooks and configuration
    haven't been initialized yet but we want to write a specific
    termination message. This scenario occurs when the vdk_main
    hook hasn't completed yet.
    :param user_error: If this is a platform error or no
    :param log: The logger which will log the exception
    :param exception: The exception
    :return:
    """
    message = ErrorMessage(
        summary=f"Plugin load failed",
        what=f"Cannot load plugin from setuptools entrypoint for group {group_name}",
        why="See exception for possible reason",
        consequences="The CLI tool will likely abort.",
        countermeasures="Re-try again. Check exception message and possibly uninstall a bad "
        "plugin (pip uninstall) "
        "Or see what plugins are installed (use `pip list` command) and if "
        "there aren't issues. "
        "Or try to reinstall the app in a new clean environment."
        "Try to revert to previous version of the CLI tool."
        "If nothing works open a SRE ticket ",
    )
    log.error(PluginException(message), exc_info=exception)
    configuration_builder = ConfigurationBuilder()
    add_definitions(configuration_builder)
    configuration_builder.add(key=LOG_CONFIG, default_value="LOCAL")

    configuration = configuration_builder.build()

    writer = TerminationMessageWriterPlugin()
    user_error_overall = user_error == ResolvableBy.USER_ERROR
    writer.write_termination_message(
        error_overall=True, user_error=user_error_overall, configuration=configuration
    )
    os._exit(0)
