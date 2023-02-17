# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.control_api_auth.auth_config import InMemAuthConfiguration
from vdk.plugin.control_api_auth.auth_exception import VDKInvalidAuthParamError
from vdk.plugin.control_api_auth.autorization_code_auth import RedirectAuthentication
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
        auth_discovery_url: str = None,
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
        :param auth_discovery_url:
            Token or Authorization URI used to exchange grant for access token.
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
        self._auth_discovery_url = auth_discovery_url
        self._auth_type = auth_type
        # Check if credentials should be cached on the local filesystem
        if cache_locally:
            self._auth = BaseAuth()
        else:
            self._auth = BaseAuth(conf=InMemAuthConfiguration())

    def authenticate(self) -> None:
        if not self._auth_type:
            raise VDKInvalidAuthParamError(
                what="Unable to log in.",
                why="auth_type was not specified.",
                consequence="Subsequent requests to Control Service will not "
                " be authenticated.",
                countermeasure="Specify what type of authentication is to be " "used.",
            )
        if not self._auth_url:
            raise VDKInvalidAuthParamError(
                what="Unable to log in.",
                why="auth_url was not specified.",
                consequence="Authentication is not possible. All subsequent "
                "requests to Control Service will not be authenticated.",
                countermeasure="Provide a valid authorization url.",
            )

        if self._auth_type == LoginTypes.API_TOKEN.value:
            self.__authenticate_with_api_token()
        elif self._auth_type == LoginTypes.CREDENTIALS.value:
            self.__authenticate_with_authorization_code()
        else:
            raise VDKInvalidAuthParamError(
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
        This type of authentication relies on pkce
        https://datatracker.ietf.org/doc/html/rfc7636
        :return:
        """
        if not self._client_id or not self._auth_discovery_url:
            raise VDKInvalidAuthParamError(
                what="Unable to log in.",
                why=f"Login type {self._auth_type} requires client_id and "
                "auth_discovery_url to be specified.",
                consequence="The authentication operation cannot be complete.",
                countermeasure="Specify client_id and auth_discovery_url and "
                "repeat the login operation.",
            )
        else:
            auth_code_flow = RedirectAuthentication(
                client_id=self._client_id,
                client_secret=self._client_secret,
                oauth2_discovery_url=self._auth_discovery_url,
                oauth2_exchange_url=self._auth_url,
                auth=self._auth,
            )
            auth_code_flow.authentication_process()
