# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import base64
import hashlib
import http
import json
import logging
import os
import re
import socket
import time
import webbrowser
from contextlib import closing
from functools import partial
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlparse

from requests import HTTPError
from requests import post
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from vdk.plugin.control_api_auth.auth_exception import VDKLoginFailedError
from vdk.plugin.control_api_auth.auth_request_values import AuthRequestValues
from vdk.plugin.control_api_auth.base_auth import BaseAuth
from vdk.plugin.control_api_auth.login_types import LoginTypes

log = logging.getLogger(__name__)


def generate_pkce_codes():
    """
    Generate PKCE code challenge and code verifier necessary during Authorization Code Workflow
    as described in RFC 7636 (see  https://tools.ietf.org/html/rfc7636)
    :return: code_verifier, code_challenge, code_challenge_method
    """
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")
    return code_verifier, code_challenge, "S256"


class LoginHandler:
    """
    Class to handle the updates of the authentication parameters and the log
    in process itself.
    """

    CODE_PARAMETER_KEY = "code"
    STATE_PARAMETER_KEY = "state"
    REFRESH_TOKEN_KEY = "refresh_token"  # nosec
    GRANT_TYPE = "authorization_code"

    def __init__(
        self,
        client_id,
        client_secret,
        exchange_endpoint,
        redirect_uri,
        code_verifier,
        auth,
    ):
        """
        :param client_id:
            The client identifier;
            See https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1
        :param client_secret:
            The client identifier;
            See https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1
        :param exchange_endpoint:
            The URL which exchanges token for access token.
        :param redirect_uri:
            URL for the authorization server to redirect back to (as defined
            in https://datatracker.ietf.org/doc/html/rfc6749#section-3.1.2).
        :param code_verifier:
            A string used to correlate the authorization request to the token
            request as described in https://tools.ietf.org/html/rfc7636
        :param auth:
            A BaseAuth object.
        """
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.exchange_endpoint: str = exchange_endpoint
        self.redirect_uri: str = redirect_uri
        self.code_verifier: str = code_verifier
        self.auth: BaseAuth = auth
        self.login_exception: Optional[Exception] = None

    def login_with_authorization_code(self, path):
        try:
            auth_code = self._acquire_auth_code(path)
            json_content = self._exchange_code_for_tokens(auth_code)
            self.auth.update_oauth2_authorization_url(self.exchange_endpoint)
            if self.REFRESH_TOKEN_KEY in json_content:
                self.auth.update_refresh_token(json_content[self.REFRESH_TOKEN_KEY])
            self.auth.update_access_token(
                json_content[AuthRequestValues.ACCESS_TOKEN_KEY.value]
            )
            self.auth.update_access_token_expiration_time(
                time.time()
                + int(json_content[AuthRequestValues.EXPIRATION_TIME_KEY.value])
            )
            self.auth.update_client_id(self.client_id)
            self.auth.update_client_secret(self.client_secret)
            self.auth.update_auth_type(LoginTypes.CREDENTIALS.value)
        except Exception as login_exception:
            self.login_exception = login_exception
            raise

    def _exchange_code_for_tokens(self, auth_code):
        headers = {
            AuthRequestValues.CONTENT_TYPE_HEADER.value: AuthRequestValues.CONTENT_TYPE_URLENCODED.value,
        }
        data = (
            f"code={auth_code}&"
            + f"grant_type={self.GRANT_TYPE}&"
            + f"redirect_uri={self.redirect_uri}"
        )
        if not self.client_secret:
            log.debug(
                "No client secret specified. We assume native app workflow with PKCE (RFC 7636)."
            )
            data = f"{data}&code_verifier={self.code_verifier}"
        basic_auth = HTTPBasicAuth(self.client_id, self.client_secret)
        try:
            response = post(
                self.exchange_endpoint, data=data, headers=headers, auth=basic_auth
            )
            response.raise_for_status()
            json_data = json.loads(response.text)
        except HTTPError as http_exception:
            raise VDKLoginFailedError(
                what="Failed to login.",
                why="HTTP error occurred during authorization workflow. "
                f"Error was: HTTP error {http_exception.response.status_code}: {http_exception.response.content}",
                consequence="Operations may not work unless previous login is still valid.",
                countermeasure="Try to login again.\n"
                "  If problem persist, try to see the reason in the why section and instruction there.\n"
                "  If that does not help, open ticket to the support team. "
                "Provide all logs you have and describe exact steps to reproduce the issue "
                "and commands executed.",
            )
        except Exception as e:
            raise VDKLoginFailedError(
                what=f"Failed to login: {str(e)}.",
                why="Problem in the configuration or service. Cannot acquire tokens.",
                consequence="Cannot login user.",
                countermeasure="Contact the owner to resolve the problem.",
            )
        return json_data

    def _acquire_auth_code(self, path):
        url = urlparse(path)
        query_components = parse_qs(url.query)
        auth_code = ""
        state = ""
        if self.CODE_PARAMETER_KEY in query_components:
            auth_code = query_components[self.CODE_PARAMETER_KEY][0]
        if self.STATE_PARAMETER_KEY in query_components:
            state = query_components[self.STATE_PARAMETER_KEY][0]
        if state != AuthRequestValues.STATE_PARAMETER_VALUE.value or not state:
            raise VDKLoginFailedError(
                what="Failed to login.",
                why="Possibly the request was intercepted.",
                consequence="Cannot login user.",
                countermeasure="Try to login again.",
            )
        if not auth_code:
            raise VDKLoginFailedError(
                what="Authentication code is empty",
                why="The user failed to authenticate properly.",
                consequence="User will not be logged in.",
                countermeasure="Try to login again.",
            )
        return auth_code


class MyHttpRequestHandler(BaseHTTPRequestHandler):
    """
    Class used by RedirectAuthentication to handle the GET redirect request in order to acquire the refresh and access
    tokens. In essence the class creates Authentication object which fills the necessary configuration fields for the
    credentials authentication type.
    """

    UTF_ENCODING = "utf8"
    CONTENT_TYPE_TEXT_HTML = "text/html"
    HTML_LOGIN_SUCCESS_TEMPLATE = (
        "<html><head></head><body><h1>Login Successful!</h1></body></html>"
    )
    HTML_LOGIN_FAILURE_TEMPLATE = "<html><head></head><body><h1>Login Failed. Check terminal for more information.</h1></body></html>"

    def __init__(self, login_handler, *args, **kwargs):
        self.login_handler = login_handler
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(http.HTTPStatus.OK)
        self.send_header(
            AuthRequestValues.CONTENT_TYPE_HEADER.value, self.CONTENT_TYPE_TEXT_HTML
        )
        self.end_headers()
        try:
            self.login_handler.login_with_authorization_code(self.path)
            self.wfile.write(bytes(self.HTML_LOGIN_SUCCESS_TEMPLATE, self.UTF_ENCODING))
        except:
            self.wfile.write(bytes(self.HTML_LOGIN_FAILURE_TEMPLATE, self.UTF_ENCODING))
            raise


class RedirectAuthentication:
    """
    Class used to start web browser and http process which will handle single GET request and shut down.
    The browser will redirect to the http process which handles the request.

    Making the port which we use for authentication constant enable integration with some OAuth2 authorization server
    (e.g VMware Cloud) which require a redirect uri when creating OAuth2 app which needs to be set to the exact
    value which is used in the redirect url. Before we took random port from the ones available which prevented us
    from configuring the URI in the application options.
    It might be good idea for this to be configurable, so we can switch to random ports when necessary
    """

    def __init__(
        self,
        client_id,
        client_secret,
        oauth2_discovery_url,
        oauth2_exchange_url,
        auth,
        redirect_uri="http://127.0.0.1",
        redirect_uri_default_port=31113,
    ):
        """

        :param client_id:
            The client identifier of the OAuth2 Application. Find out more https://tools.ietf.org/html/rfc6749#section-2.3.1
        :param client_secret:
            The client secret of the OAuth2 Application. Find out more https://tools.ietf.org/html/rfc6749#section-2.3.1
        :param oauth2_discovery_url:
            Token or Authorization URI used to exchange grant for access token
        :param oauth2_exchange_url:
            The URL which exchanges token for access token.
        :param auth:
            A BaseAuth object.
        :param redirect_uri:
            The redirect uri which will be used in Authorization Workflow.
            Per https://tools.ietf.org/html/rfc8252#section-7.3 it should be http://127.0.0.1
            so there should not be reason to override the default except for tests
        :param redirect_uri_default_port:
            The default port to use for redirect uri unless env. variable 'OAUTH2_REDIRECT_URI_PORT' is used.
            If None - then random one is assigned
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.oauth2_discovery_url = oauth2_discovery_url
        self.oauth2_exchange_url = oauth2_exchange_url
        self.auth = auth

        env_port = os.getenv("OAUTH2_REDIRECT_URI_PORT", default=None)
        if env_port:
            self.port = int(env_port)
        elif redirect_uri_default_port is not None:
            self.port = redirect_uri_default_port
        else:
            self.port = self.find_free_port()
        self.redirect_uri = f"{redirect_uri}:{self.port}"

        (
            self.code_verifier,
            self.code_challenge,
            self.code_challenge_method,
        ) = generate_pkce_codes()

    def authentication_process(self):
        authorization_url = self._create_authorization_redirect_url()
        discovery_endpoint = authorization_url[0]
        login_handler = self._create_login_handler()
        handler = self._create_redirect_handler(login_handler)
        self._redirect(discovery_endpoint, handler, login_handler)

    def _redirect(self, discovery_endpoint: str, handler, login_handler: LoginHandler):
        with HTTPServer(("", self.port), handler) as server:
            print(f"Opening browser at:\n{discovery_endpoint}")
            is_open = webbrowser.open(discovery_endpoint)
            if not is_open:
                print(
                    "We failed to open the browser automatically and will proceed to login manually.\n"
                    "Please, follow below instructions:"
                )
                self._manual_login(discovery_endpoint, login_handler)
            else:  # TODO: that's not very good UX, let's timeout after 1 minute
                print(
                    "Press [Ctrl + C]/[Command + C] to quit in case of error in the browser."
                )
                server.handle_request()
                if login_handler.login_exception:
                    raise login_handler.login_exception

    @staticmethod
    def _create_redirect_handler(login_handler: LoginHandler):
        return partial(MyHttpRequestHandler, login_handler)

    def _create_login_handler(self) -> LoginHandler:
        return LoginHandler(
            client_id=self.client_id,
            client_secret=self.client_secret,
            exchange_endpoint=self.oauth2_exchange_url,
            redirect_uri=self.redirect_uri,
            code_verifier=self.code_verifier,
            auth=self.auth,
        )

    def _create_authorization_redirect_url(self):
        oauth = OAuth2Session(client_id=self.client_id, redirect_uri=self.redirect_uri)
        if not self.client_secret:
            log.debug(
                "No client secret specified. We assume native app workflow with PKCE (RFC 7636)."
            )
            return oauth.authorization_url(
                self.oauth2_discovery_url,
                state=AuthRequestValues.STATE_PARAMETER_VALUE.value,
                prompt=AuthRequestValues.LOGIN_PROMPT.value,
                code_challenge=self.code_challenge,
                code_challenge_method=self.code_challenge_method,
            )
        else:
            return oauth.authorization_url(
                self.oauth2_discovery_url,
                state=AuthRequestValues.STATE_PARAMETER_VALUE.value,
                prompt=AuthRequestValues.LOGIN_PROMPT.value,
            )

    @staticmethod
    def find_free_port():
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(("", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def _manual_login(self, discovery_endpoint, handler: LoginHandler):
        # TODO: Replace the print statements with something more user friendly.
        # manual login is necessary for environment where there is not a browser -
        # console only OS environment, WSL (Windows subsystem for linux)
        print(
            f"Copy paste the following link in your browser:\n\n{discovery_endpoint}\n\n"
        )
        print("Login using your company credentials and wait all redirects to finish.")
        print(
            f"The last redirect will be to a page that starts with {self.redirect_uri} - "
            "the page may show an error that site cannot be reached which you can ignore.\n"
        )
        print(
            f"Please, copy the address that the browser was redirected to (it should start with {self.redirect_uri}) and paste it here:"
        )
        url = str(input("Copy-pasted URL: ")).strip()
        handler.login_with_authorization_code(url)
