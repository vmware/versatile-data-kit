# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
import os
from logging import Logger
from typing import Any
from typing import List
from typing import Optional

from vdk.internal.builtin_plugins.config.vdk_config import LOG_CONFIG
from vdk.internal.builtin_plugins.termination_message.writer import (
    TerminationMessageWriterPlugin,
)
from vdk.internal.builtin_plugins.termination_message.writer_configuration import (
    add_definitions,
)
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder


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
    error_overall: bool, user_error: bool, log: Logger, exception: Exception
):
    """
    Write a termination message and exit with specified error.
    Intended for use in cases when hooks and configuration
    haven't been initialized yet but we want to write a specific
    termination message. This scenario occurs when the vdk_main
    hook hasn't completed yet.
    :return:
    """
    log.error(exception)
    configuration_builder = ConfigurationBuilder()
    add_definitions(configuration_builder)
    configuration_builder.add(key=LOG_CONFIG, default_value="LOCAL")

    configuration = configuration_builder.build()

    writer = TerminationMessageWriterPlugin()
    writer.write_termination_message(error_overall, user_error, configuration, False)
    os._exit(0)
