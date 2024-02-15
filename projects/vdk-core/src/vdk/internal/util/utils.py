# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
from logging import Logger
from typing import Any
from typing import List
from typing import Optional

from vdk.internal.core import errors
from vdk.internal.core.config import Configuration
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


def log_plugin_load_fail(
    user_error: ResolvableBy, log: Logger, exception: Exception, group_name
):
    """
    Logs errors during plugin load. Calls the errors.log_exception() method
    which will also update the resolvable context of the VDK run.

    :param user_error: If this is a platform error or no
    :param log: The logger which will log the exception
    :param exception: The exception
    :param group_name
    :return:
    """
    errors.report(user_error, exception)
    errors.log_exception(
        log,
        exception,
        f"Cannot load plugin from setuptools entrypoint for group {group_name}",
        "See exception for possible reason",
        "The CLI tool will likely abort.",
        "Re-try again. Check exception message and possibly uninstall a bad"
        " plugin (pip uninstall) Or see what plugins are installed (use `pip"
        " list` command) and if there aren't issues. Or try to reinstall the"
        " app in a new clean environment. Try to revert to previous version of"
        " the CLI tool. If nothing works open a SRE ticket.",
    )
