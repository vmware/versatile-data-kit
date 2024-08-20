# Copyright 2024-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import base64
import json
import logging
import os
from typing import List

import requests
import taurus_datajob_api
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.plugin.control_api_auth.auth_config import LocalFolderCredentialsCache
from vdk.plugin.oauth.oauth_configuration import add_definitions

log = logging.getLogger(__name__)

CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"
TEAM_CLIENT_ID = "TEAM_CLIENT_ID"
TEAM_CLIENT_SECRET = "TEAM_CLIENT_SECRET"
CONTROL_SERVICE_REST_API_URL = "CONTROL_SERVICE_REST_API_URL"
API_TOKEN_AUTHORIZATION_URL = "API_TOKEN_AUTHORIZATION_URL"
CSP_AUTHORIZATION_URL = "CSP_AUTHORIZATION_URL"
CSP_ACCESS_TOKEN = "CSP_ACCESS_TOKEN"
DISABLE_OAUTH_LOGIN = "DISABLE_OAUTH_LOGIN"


class OauthPlugin:
    def __init__(self):
        self.control_service_rest_api_url = None
        self.access_token = None
        self.team_name = None
        self.is_oauth_creds_available = False

    def __attempt_oauth_authentication(self, context: JobContext):
        original_string = (
            context.core_context.configuration.get_value(CLIENT_ID)
            + ":"
            + context.core_context.configuration.get_value(CLIENT_SECRET)
        )

        # Encoding
        encoded_bytes = base64.b64encode(original_string.encode("utf-8"))
        encoded_string = encoded_bytes.decode("utf-8")

        url = context.core_context.configuration.get_value(CSP_AUTHORIZATION_URL)
        headers = {
            "Authorization": "Basic " + encoded_string,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        response = requests.post(url, headers=headers, data=data)
        response_json = json.loads(response.text)
        os.environ[CSP_ACCESS_TOKEN] = response_json["access_token"]

    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder)

    @hookimpl
    def vdk_initialize(self, context: CoreContext) -> None:
        """
        Check if Oauth enabled
        """
        disable_oauth = os.getenv(DISABLE_OAUTH_LOGIN).lower() == "true"
        if disable_oauth:
            return
        # Scenario: data job running in cloud has oauth creds present
        if (
            os.getenv(TEAM_CLIENT_ID) is not None
            and os.getenv(TEAM_CLIENT_SECRET) is not None
        ):
            self.is_oauth_creds_available = True
            return
        # Scenario: data job running in local does not have oauth creds
        credentials_cache = LocalFolderCredentialsCache()
        credentials = credentials_cache.read_credentials()
        credentials = json.loads(credentials.replace("'", '"'))
        self.access_token = credentials.get("access_token")
        self.control_service_rest_api_url = context.configuration.get_value(
            CONTROL_SERVICE_REST_API_URL
        )
        self.team_name = context.configuration.get_value("team")

    @hookimpl(tryfirst=True)
    def initialize_job(self, context: JobContext) -> None:
        """
        This is called during vdk run (job execution)
        Check if Oauth enabled
        """
        disable_oauth = os.getenv(DISABLE_OAUTH_LOGIN).lower() == "true"
        if disable_oauth:
            return
        if self.is_oauth_creds_available:
            context.core_context.configuration.override_value(
                "client_id", os.getenv(TEAM_CLIENT_ID)
            )
            context.core_context.configuration.override_value(
                "client_secret", os.getenv(TEAM_CLIENT_SECRET)
            )
        else:
            # Enter a context with an instance of the API client
            configuration = taurus_datajob_api.Configuration(
                host=self.control_service_rest_api_url,
            )

            configuration.access_token = self.access_token
            oauth_creds = None
            with taurus_datajob_api.ApiClient(configuration) as api_client:
                api_instance = taurus_datajob_api.DataJobsSecretsApi(api_client)
                try:
                    # Retrieves details of an existing Data Job by specifying the name of the Data Job. | (Stable)
                    oauth_creds = api_instance.oauth_credentials_get(self.team_name)
                except Exception as e:
                    print(
                        "Exception when calling DataJobsSecretsApi->oauth_credentials_get: %s\n"
                        % e
                    )
                    raise e
            oauth_creds = oauth_creds.to_dict()
            context.core_context.configuration.override_value(
                "client_id", oauth_creds.get("clientId")
            )
            context.core_context.configuration.override_value(
                "client_secret", oauth_creds.get("clientSecret")
            )

        self.__attempt_oauth_authentication(context)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(OauthPlugin())
