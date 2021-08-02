# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
from typing import Any


def class_fqname(py_object: Any) -> str:
    """
    :param py_object: Any python object
    :return: the full qualified name of the class (package.package.classname)
    """
    module = inspect.getmodule(py_object)
    if module is None:
        return py_object.__class__.__name__
    return f"{py_object.__class__.__module__}.{py_object.__class__.__name__}"
