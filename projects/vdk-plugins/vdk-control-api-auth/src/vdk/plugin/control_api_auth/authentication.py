# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import warnings
from typing import Optional

from vdk.plugin.control_api_auth.auth_config import CredentialsCache
from vdk.plugin.control_api_auth.auth_config import LocalFolderCredentialsCache
from vdk.plugin.control_api_auth.auth_config import SingletonInMemoryCredentialsCache
from vdk.plugin.control_api_auth.auth_exception import VDKInvalidAuthParamError
from vdk.plugin.control_api_auth.autorization_code_auth import RedirectAuthentication
from vdk.plugin.control_api_auth.base_auth import BaseAuth
from vdk.plugin.control_api_auth.login_types import LoginTypes

log = logging.getLogger(__name__)


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
        cache_locally: bool = None,
        possible_jwt_user_keys=None,
        credentials_cache: CredentialsCache = LocalFolderCredentialsCache(),
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
            Deprecated: use credentials_cache instead to pass how credentials are stored explicitly.
        :param possible_jwt_user_keys:
            Used by get_authenticated_username to try to discover correct username if OAuth2 and JWT token is used. It is a list of keys where the first existing key in a JTW token is returned.
            Defaults to some common user keys.
        :param credentials_cache:
            The configuration store used to actually store the credentials
        """
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = token
        self._auth_url = authorization_url
        self._auth_discovery_url = auth_discovery_url
        self._auth_type = auth_type

        if cache_locally is not None:
            warnings.warn(
                "Authentication constructor cache_locally argument is deprecated. "
                "Use credentials_cache to pass explicitly the credential cache store."
            )
            credentials_cache = (
                LocalFolderCredentialsCache()
                if cache_locally
                else SingletonInMemoryCredentialsCache()
            )

        self._auth = BaseAuth(credentials_cache)

        if possible_jwt_user_keys:
            self._possible_jwt_user_keys = possible_jwt_user_keys
        else:  # sensible defaults
            self._possible_jwt_user_keys = [
                "username",
                "acct",
                "preferred_username",
                "email",
            ]

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

    def get_authenticated_username(self) -> Optional[str]:
        """
        Extract user name about currently authenticated user.
        It tries to get username or if not available user email or if that fails some user id.
        The reponse format should not be relied upon, it's meant to be used for logging and telemetry.
        """
        if self._username:
            return self._username

        if not self._token:
            try:
                self._token = self.read_access_token()
            except Exception:
                log.debug(f"Could not to read access token.", exc_info=True)
        if not self._token:
            self._token = self._auth.read_cached_access_token_only()
        if not self._token:
            return None

        try:
            import jwt

            jwt_payload = jwt.decode(self._token, options={"verify_signature": False})
            if not jwt_payload:
                return None

            for key in self._possible_jwt_user_keys:
                user_id = jwt_payload.get(key)
                if user_id:
                    return user_id

        except Exception:
            log.debug(
                f"Could not to extract user information from the token.", exc_info=True
            )
            return None

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
