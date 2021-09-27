# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from vdk.internal.control.auth.auth import Authentication
from vdk.internal.control.auth.login_types import LoginTypes
from vdk.internal.control.configuration.vdk_config import VDKConfig


class ApiKeyAuthentication:
    """
    Class that execute authentication process using API token.
    It will use the API token to get temporary access token using api token authorization URL.
    See Authentication class as well.
    """

    def __init__(
        self,
        api_token_authorization_url: Optional[str] = None,
        api_token: Optional[str] = None,
    ):
        """
        :param api_token_authorization_url: Authorization URL - Same as login --api-token-authorization-server-url.
        :param api_token: API Token - Same as login --api-token.
        """
        self.__api_token = api_token
        self.__api_token_authorization_url = api_token_authorization_url
        self.__auth = Authentication()

    def authentication_process(self) -> None:
        """
        Executes the authentication process and caches the generated access token so it can be used during REST calls.
        """
        self.__auth.update_api_token_authorization_url(
            self.__api_token_authorization_url
        )
        self.__auth.update_api_token(self.__api_token)
        self.__auth.update_auth_type(LoginTypes.API_TOKEN.value)
        self.__auth.acquire_and_cache_access_token()
