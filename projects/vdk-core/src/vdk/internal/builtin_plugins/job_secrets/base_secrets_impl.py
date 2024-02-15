# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0


def check_valid_secret(k: str, v: str, supported_types=None) -> None:
    """
    Check if secret key and value are valid
    """

    if supported_types is None:
        supported_types = []

    if str != type(k) or k.strip() != k or "".join(k.split()) != k:
        msg = (
            f"Secret {k} is of unsupported type or has unsupported name. "
            f"Only string secrets with no whitespaces in the name are supported."
        )
        raise ValueError(msg)

    if not supported_types:
        supported_types = [int, float, str, list, type(None)]

    if type(v) not in supported_types:
        msg = (
            f"Value for secret  {k} is of unsupported type {type(v)}. "
            f"Only int, float, str, list, and NoneType types are supported. "
        )
        raise ValueError(msg)
