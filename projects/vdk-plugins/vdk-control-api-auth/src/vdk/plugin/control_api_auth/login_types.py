# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from enum import Enum


class LoginTypes(Enum):
    """
    An enum used to store the types of authentication which the
    versatile data kit sdk (vdk) provides.
    """

    CREDENTIALS = "credentials"
    API_TOKEN = "api-token"  # nosec
