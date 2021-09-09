# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from enum import Enum


class AuthRequestValues(Enum):
    """
    An enum used to the common values used in the redirect logic.
    """

    STATE_PARAMETER_VALUE = "requested"
    LOGIN_PROMPT = "login"
    CONTENT_TYPE_URLENCODED = "application/x-www-form-urlencoded"
    REFRESH_TOKEN_GRANT_TYPE = "refresh_token"  # nosec
    CONTENT_TYPE_HEADER = "Content-Type"
    EXPIRATION_TIME_KEY = "expires_in"
    ACCESS_TOKEN_KEY = "access_token"  # nosec
