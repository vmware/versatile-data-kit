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
from vdk.plugin.oauth.oauth_configuration import OauthPluginConfiguration


log = logging.getLogger(__name__)

TEAM_CLIENT_ID = "TEAM_CLIENT_ID"
TEAM_CLIENT_SECRET = "TEAM_CLIENT_SECRET"
TEAM_ACCESS_TOKEN = "TEAM_ACCESS_TOKEN"


class OauthPlugin:
    def __init__(self):
        self.is_oauth_creds_available = False

    def __attempt_oauth_authentication(
        self, oauth_configuration: OauthPluginConfiguration
    ):
        original_string = (
            oauth_configuration.team_client_id()
            + ":"
            + oauth_configuration.team_client_secret()
        )

        # Encoding
        encoded_bytes = base64.b64encode(original_string.encode("utf-8"))
        encoded_string = encoded_bytes.decode("utf-8")

        url = oauth_configuration.team_oauth_authorize_url()
        headers = {
            "Authorization": "Basic " + encoded_string,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        response = requests.post(url, headers=headers, data=data)
        response_json = json.loads(response.text)
        os.environ[TEAM_ACCESS_TOKEN] = response_json["access_token"]

    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder)

    @hookimpl
    def vdk_initialize(self, context: CoreContext) -> None:
        """
        Check if Oauth enabled
        """
        oauth_configuration = OauthPluginConfiguration(context.configuration)

        if oauth_configuration.disable_oauth_plugin():
            return

    @hookimpl(tryfirst=True)
    def initialize_job(self, context: JobContext) -> None:
        """
        This is called during vdk run (job execution)
        Check if Oauth enabled
        """
        oauth_configuration = OauthPluginConfiguration(
            context.core_context.configuration
        )

        if oauth_configuration.disable_oauth_plugin():
            return

        # Scenario: data job running in local does not have oauth creds
        if (
            oauth_configuration.team_client_id() is None
            or oauth_configuration.team_client_secret() is None
        ):
            credentials_cache = LocalFolderCredentialsCache()
            credentials = credentials_cache.read_credentials()
            try:
                creds_json = json.loads(credentials)
            except json.JSONDecodeError as e:
                log.error(f"Try VDK login command and then try executing data job.")
                raise e
            access_token = creds_json.get("access_token")
            team_name = oauth_configuration.team()
            # Enter a context with an instance of the API client
            configuration = taurus_datajob_api.Configuration(
                host=oauth_configuration.control_service_rest_api_url(),
            )

            configuration.access_token = access_token
            oauth_creds = None
            with taurus_datajob_api.ApiClient(configuration) as api_client:
                api_instance = taurus_datajob_api.DataJobsSecretsApi(api_client)
                try:
                    # Retrieves details of an existing Data Job by specifying the name of the Data Job. | (Stable)
                    oauth_creds = api_instance.oauth_credentials_get(team_name)
                except Exception as e:
                    log.error(f"Exception when fetching oauth credentials: {e}")
                    raise e
            oauth_creds = oauth_creds.to_dict()

            context.core_context.configuration.override_value(
                TEAM_CLIENT_ID, oauth_creds.get("clientId")
            )
            context.core_context.configuration.override_value(
                TEAM_CLIENT_SECRET, oauth_creds.get("clientSecret")
            )

        self.__attempt_oauth_authentication(oauth_configuration)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(OauthPlugin())
