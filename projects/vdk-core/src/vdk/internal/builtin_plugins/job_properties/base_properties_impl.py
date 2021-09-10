# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List
from typing import Type


def check_valid_property(k: str, v: str, supported_types: List[Type] = []) -> None:
    """
    Check if property key and value are valid
    """
    if str != type(k) or k.strip() != k or "".join(k.split()) != k:
        msg = (
            f"Property {k} is of unsupported type or has unsupported name. "
            f"Only string properties with no whitespaces in the name are supported."
        )
        raise ValueError(msg)

    if not supported_types:
        supported_types = [int, float, str, list, type(None)]

    if type(v) not in supported_types:
        msg = (
            f"Value {v} for property {k} is of unsupported type {type(v)}. "
            f"Only int, float, str, list, and NoneType types are supported. "
        )
        raise ValueError(msg)
