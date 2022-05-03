# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.control_api_auth.auth_config import InMemAuthConfiguration
from vdk.plugin.control_api_auth.auth_exception import VDKAuthException
from vdk.plugin.control_api_auth.base_auth import BaseAuth
from vdk.plugin.control_api_auth.login_types import LoginTypes


class Authentication:
    """Main class used for authentication."""

    def __init__(
        self,
        username: str = None,
        password: str = None,
        client_id: str = None,
        client_secret: str = None,
        token: str = None,
        authorization_url: str = None,
        auth_type: str = None,
        cache_locally: bool = False,
    ):
        """
        :param username: A user's username in case basic authentication is used.
        :param password: A user's password in case basic authentication is used.
        :param client_id:
            The client identifier;
            See https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1
        :param client_secret:
            The client identifier;
            See https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1
        :param token:
            OAuth api token or a refresh token as specified in
            https://datatracker.ietf.org/doc/html/rfc6749#section-1.5 and used
            to obtain access token from the authorization server.
        :param authorization_url:
            The URL which exchanges token for access token.
        :param auth_type:
            What type of authentication should be used (e.g., refresh_token,
            basic_auth, etc.).
        :param cache_locally:
            A flag, indicating if credentials should be cached locally (in a
            file).
        """
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = token
        self._auth_url = authorization_url
        self._auth_type = auth_type
        # Check if credentials should be cached on the local filesystem
        if cache_locally:
            self._auth = BaseAuth()
        else:
            self._auth = BaseAuth(conf=InMemAuthConfiguration())

    def authenticate(self) -> None:
        if not self._auth_type:
            raise VDKAuthException(
                what="Unable to log in.",
                why="auth_type was not specified.",
                consequence="Subsequent requests to Control Service will not "
                " be authenticated.",
                countermeasure="Specify what type of authentication is to be " "used.",
            )
        if not self._auth_url:
            raise VDKAuthException(
                what="Unable to log in.",
                why="auth_url was not specified.",
                consequence="Authentication is not possible. All subsequent "
                "requests to Control Service will not be authenticated.",
                countermeasure="Provide a valid authorization url.",
            )

        if self._auth_type == LoginTypes.API_TOKEN.value:
            self.__authenticate_with_api_token()
        else:
            raise VDKAuthException(
                what="Unexpected authentication type.",
                why=f"Unknown auth_type {self._auth_type} was used.",
                consequence="Authentication is not possible.",
                countermeasure="Provide a valid auth_type.",
            )

    def read_access_token(self):
        """Read access token from cache."""
        return self._auth.read_access_token()

    def __authenticate_with_api_token(self):
        """Authenticate by providing only a OAuth2 API token."""
        self._auth.update_api_token_authorization_url(
            api_token_authorization_url=self._auth_url
        )
        self._auth.update_api_token(api_token=self._token)
        self._auth.update_auth_type(auth_type=LoginTypes.API_TOKEN.value)
        self._auth.acquire_and_cache_access_token()

    # NOTE: Implementation to be added with subsequent PR
    def __authenticate_with_authorization_code(self):
        """
        Authenticate with authorization code as described in
        https://datatracker.ietf.org/doc/html/rfc6749#section-1.3.1
        :return:
        """
        raise NotImplementedError("This method is yet to be implemented.")
