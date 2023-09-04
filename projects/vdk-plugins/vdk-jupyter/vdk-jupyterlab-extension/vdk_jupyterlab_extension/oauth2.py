# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import time
from urllib.parse import urlparse
from urllib.parse import urlunparse

import requests
from jupyter_server.base.handlers import APIHandler
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from vdk.plugin.control_api_auth.auth_request_values import AuthRequestValues
from vdk.plugin.control_api_auth.autorization_code_auth import generate_pkce_codes
from vdk.plugin.control_api_auth.base_auth import BaseAuth
from vdk_jupyterlab_extension import VdkJupyterConfig

log = logging.getLogger(__name__)


class OAuth2Handler(APIHandler):
    def initialize(self, vdk_config: VdkJupyterConfig):
        log.info(f"VDK config: {vdk_config.__dict__}")

        self._authorization_url = vdk_config.oauth2_authorization_url
        self._access_token_url = vdk_config.oauth2_token_url
        self._client_id = vdk_config.oauth2_client_id
        self._redirect_url = vdk_config.oauth2_redirect_url

        log.info(f"Authorization URL: {self._authorization_url}")
        log.info(f"Access Token URL: {self._access_token_url}")
        # log.info(f"client_id: {self._client_id}")

        # No client secret. We use only native app workflow with PKCE (RFC 7636)

    @staticmethod
    def _fix_localhost(uri: str):
        """
        This is added for local testing. Oauthorization Providers generally allow 127.0.0.1 to be registered as redirect URL
        so we change localhost to 127.0.0.1
        :param uri:
        :return:
        """
        parsed_uri = urlparse(uri)

        if parsed_uri.hostname == "localhost":
            netloc = parsed_uri.netloc.replace("localhost", "127.0.0.1")
            modified_uri = parsed_uri._replace(netloc=netloc, query="")
            return urlunparse(modified_uri)
        else:
            modified_uri = parsed_uri._replace(query="")
            return urlunparse(modified_uri)

    def get(self):
        # TODO: this is duplicating a lot of the code in vdk-control-api-auth
        # https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-control-api-auth
        # But that module is written with focus on CLI usage a bit making it harder to reuse
        # and it needs to be refactored first.
        redirect_url = self._redirect_url
        if not redirect_url:
            redirect_url = self.request.full_url()
        redirect_url = self._fix_localhost(redirect_url)

        log.info(f"redirect uri is {redirect_url}")

        if self.get_argument("code", None):
            log.info(
                "Authorization code received. Will generate access token using authorization code."
            )
            tokens = self._exchange_auth_code_for_access_token(redirect_url)
            log.info(f"Got tokens data: {tokens}")  # TODO: remove this
            self._persist_tokens_data(tokens)
        else:
            log.info(f"Authorization URL is: {self._authorization_url}")
            full_authorization_url = self._prepare_authorization_code_request_url(
                redirect_url
            )
            self.finish(full_authorization_url)

    def _persist_tokens_data(self, tokens):
        auth = BaseAuth()
        auth.update_oauth2_authorization_url(self._access_token_url)
        auth.update_client_id(self._client_id)
        auth.update_access_token(tokens.get(AuthRequestValues.ACCESS_TOKEN_KEY.value))
        auth.update_access_token_expiration_time(
            time.time() + int(tokens[AuthRequestValues.EXPIRATION_TIME_KEY.value])
        )
        if AuthRequestValues.REFRESH_TOKEN_GRANT_TYPE in tokens:
            auth.update_refresh_token(
                tokens.get(AuthRequestValues.REFRESH_TOKEN_GRANT_TYPE)
            )

    def _prepare_authorization_code_request_url(self, redirect_uri):
        (code_verifier, code_challenge, code_challenge_method) = generate_pkce_codes()
        self.application.settings["code_verifier"] = code_verifier
        oauth = OAuth2Session(client_id=self._client_id, redirect_uri=redirect_uri)
        full_authorization_url = oauth.authorization_url(
            self._authorization_url,
            state="requested",
            prompt=AuthRequestValues.LOGIN_PROMPT.value,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )[0]
        return full_authorization_url

    def _exchange_auth_code_for_access_token(self, redirect_uri) -> dict:
        code = self.get_argument("code")
        headers = {
            AuthRequestValues.CONTENT_TYPE_HEADER.value: AuthRequestValues.CONTENT_TYPE_URLENCODED.value,
        }
        code_verifier = self.application.settings["code_verifier"]

        data = (
            f"code={code}&"
            + f"grant_type=authorization_code&"
            + f"code_verifier={code_verifier}&"
            f"redirect_uri={redirect_uri}"
        )
        basic_auth = HTTPBasicAuth(self._client_id, "")
        try:
            # TODO : this should be async io
            response = requests.post(
                self._access_token_url, data=data, headers=headers, auth=basic_auth
            )
            if response.status_code >= 400:
                log.error(
                    f"Request to {self._access_token_url} with data {data} returned {response.status_code}\n"
                    rf"Reason: {response.reason}\dn"
                    f"Response content: {response.content}\n"
                    f"Response headers: {response.headers}"
                )

            json_data = json.loads(response.text)
            return json_data
        except Exception as e:
            log.exception(e)
