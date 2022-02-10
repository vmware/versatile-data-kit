# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
from typing import Any
from typing import List
from typing import Optional

from vdk.internal.core.config import Configuration


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
