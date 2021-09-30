# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import time
from typing import Optional

from requests import post
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from vdk.internal.control.auth.auth_request_values import AuthRequestValues
from vdk.internal.control.auth.login_types import LoginTypes
from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.internal.control.configuration.vdk_config import VDKConfigFolder
from vdk.internal.control.exception.vdk_exception import VDKException

log = logging.getLogger(__name__)


class AuthenticationCache:
    """
    Class used to keep the fields in the vdk-cred.json file from which authorization and authentication
    tokens can be taken
    """

    def __init__(
        self,
        authorization_url=None,
        refresh_token=None,
        access_token=None,
        access_token_expiration_time=0,
        client_id="not-used",
        client_secret="not-used",
        api_token=None,
        api_token_authorization_url=None,
        auth_type=None,
        **ignored_kwargs,
    ):
        """

        :param authorization_url:
            Token or Authorization URI used to exchange grant for access token
        :param refresh_token:
            Used in refresh token grant type flow; See https://tools.ietf.org/html/rfc6749#section-1.5
        :param access_token:
            Cached access token used during requests; See https://tools.ietf.org/html/rfc6749#section-1.4
        :param access_token_expiration_time:
            When the access token expires (epoch seconds - same as time.time() return)
        :param client_id:
            The client identifier; See https://tools.ietf.org/html/rfc6749#section-2.3.1
        :param api_token:
            Token used to grant access to the API, including exchange for access token
        :param api_token_authorization_url:
            The URL which exchanges api_token for access token
        """
        #
        self.authorization_url = authorization_url
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.access_token_expiration_time = access_token_expiration_time
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_token = api_token
        self.api_token_authorization_url = api_token_authorization_url
        self.auth_type = auth_type

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class AuthenticationCacheSerDe:
    @staticmethod
    def serialize(cache):
        return json.dumps(cache.__dict__)

    @staticmethod
    def deserialize(content: str):
        if content:
            return AuthenticationCache(**json.loads(content))
        else:
            return AuthenticationCache()


class Authentication:
    REFRESH_TOKEN_GRANT_TYPE = "refresh_token"  # nosec

    def __init__(self, conf=VDKConfigFolder(), vdk_config=VDKConfig()):
        self._conf = conf
        self.__vdk_config = vdk_config
        self._cache = self.__load_cache()

    def __load_cache(self):
        content = self._conf.read_credentials()
        return AuthenticationCacheSerDe.deserialize(content)

    def __update_cache(self):
        self._conf.save_credentials(AuthenticationCacheSerDe.serialize(self._cache))

    def __exchange_api_for_access_token(self):
        try:
            log.debug(
                f"Refresh API token against {self._cache.api_token_authorization_url} "
            )
            client = OAuth2Session()
            token_response = client.refresh_token(
                self._cache.api_token_authorization_url,
                refresh_token=self._cache.api_token,
            )
            log.debug(
                f"Token response received: "
                f"token_type: {token_response.get('token_type', None)}; "
                f"expires_in: {token_response.get('expires_in', None)}; "
                f"scope: {token_response.get('scope', None)}"
            )
        except Exception as e:
            raise VDKException(
                what="Failed to login",
                why=f"Authorization server at {self._cache.api_token_authorization_url} returned error: {str(e)}",
                consequence="Your credentials are not refreshed and VDK CLI operations that require authentication "
                "will not work.",
                countermeasure="Check error message and follow instructions in it. Check your network connectivity."
                " Check if you can access the Oauth2 server. Retry to login a few times again."
                " Contact SRE Team operating Oauth2 server for help if nothing else works.",
            ) from e
        # Response per spec in https://tools.ietf.org/html/rfc6750#section-4
        # see also https://www.oauth.com/oauth2-servers/access-tokens/access-token-response
        self.update_access_token(
            token_response[AuthRequestValues.ACCESS_TOKEN_KEY.value]
        )
        self.update_access_token_expiration_time(
            time.time()
            + int(token_response.get(AuthRequestValues.EXPIRATION_TIME_KEY.value, "0"))
        )

    def read_access_token(self) -> Optional[str]:
        """
        Read access token from _cache or fetch it from Authorization server.
        If not available in _cache it will get it using provided configuration during VDK CLI login to fetch it.
        If it detects that token is about to expire it will try to refresh it.
        :return: the access token or None if it cannot detect any credentials.
        """
        if (
            not self._cache.access_token
            or self._cache.access_token_expiration_time < time.time() + 60
        ):
            log.debug("Acquire access token (it's either expired or missing) ...")
            self.acquire_and_cache_access_token()
        return self._cache.access_token

    def acquire_and_cache_access_token(self):
        """
        Acquires and caches access token
        """
        log.debug(f"Using auth type {self._cache.auth_type} to acquire access token")
        if (
            self._cache.auth_type == LoginTypes.API_TOKEN.value
            and self._configured_api_token()
        ):
            self.__exchange_api_for_access_token()
        elif (
            self._cache.auth_type == LoginTypes.CREDENTIALS.value
            and self._configured_refresh_token()
        ):
            self.__exchange_refresh_for_access_token()
        elif (
            self.__vdk_config.api_token
            and self.__vdk_config.api_token_authorization_url
        ):
            self.update_api_token(self.__vdk_config.api_token)
            self.update_api_token_authorization_url(
                self.__vdk_config.api_token_authorization_url
            )
            self.__exchange_api_for_access_token()
        else:
            log.debug(
                "No authentication mechanism found. Will not cache access token."
                "If Control Service authentication is enabled, API calls will fail."
            )

    def __exchange_refresh_for_access_token(self):
        basic_auth = HTTPBasicAuth(self._cache.client_id, self._cache.client_secret)
        headers = {
            AuthRequestValues.CONTENT_TYPE_HEADER.value: AuthRequestValues.CONTENT_TYPE_URLENCODED.value,
        }
        data = (
            f"grant_type={self.REFRESH_TOKEN_GRANT_TYPE}&"
            + f"refresh_token={self._cache.refresh_token}"
        )
        log.debug(
            f"Refresh access token against {self._cache.authorization_url} grant_type={self.REFRESH_TOKEN_GRANT_TYPE}"
        )
        response = post(
            self._cache.authorization_url, data=data, headers=headers, auth=basic_auth
        )
        json_data = json.loads(response.text)
        log.debug(
            f"Refresh access token response received: status: {response.status_code}"
        )
        self.update_access_token(json_data[AuthRequestValues.ACCESS_TOKEN_KEY.value])
        self.update_access_token_expiration_time(
            time.time() + int(json_data[AuthRequestValues.EXPIRATION_TIME_KEY.value])
        )

    def update_api_token_authorization_url(self, api_token_authorization_url):
        """
        Updates and caches authorization URL
        """
        self._cache.api_token_authorization_url = api_token_authorization_url
        self.__update_cache()

    def update_api_token(self, api_token):
        """
        Updates and caches refresh token
        """
        self._cache.api_token = api_token
        self.__update_cache()

    def update_refresh_token(self, refresh_token):
        """
        Updates and caches refresh token
        """
        self._cache.refresh_token = refresh_token
        self.__update_cache()

    def update_client_id(self, client_id):
        """
        Updates and caches refresh token
        """
        self._cache.client_id = client_id
        self.__update_cache()

    def update_client_secret(self, client_secret):
        """
        Updates and caches refresh token
        """
        self._cache.client_secret = client_secret
        self.__update_cache()

    def update_access_token(self, access_token):
        """
        Updates and caches refresh token
        """
        self._cache.access_token = access_token
        self.__update_cache()

    def update_access_token_expiration_time(self, access_token_expiration_time):
        """
        Updates and caches refresh token
        """
        self._cache.access_token_expiration_time = access_token_expiration_time
        self.__update_cache()

    def update_oauth2_authorization_url(self, authorization_url):
        self._cache.authorization_url = authorization_url
        self.__update_cache()

    def update_auth_type(self, auth_type):
        self._cache.auth_type = auth_type
        self.__update_cache()

    def _configured_api_token(self):
        return self._cache.api_token and self._cache.api_token_authorization_url

    def _configured_refresh_token(self):
        return (
            self._cache.refresh_token
            and self._cache.authorization_url
            and self._cache.client_id
            and self._cache.client_secret
        )
