# Copyright 2024-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"
TEAM_CLIENT_ID = "TEAM_CLIENT_ID"
TEAM_CLIENT_SECRET = "TEAM_CLIENT_SECRET"
CONTROL_SERVICE_REST_API_URL = "CONTROL_SERVICE_REST_API_URL"
API_TOKEN_AUTHORIZATION_URL = "API_TOKEN_AUTHORIZATION_URL"
TEAM_OAUTH_AUTHORIZE_URL = "TEAM_OAUTH_AUTHORIZE_URL"
CSP_ACCESS_TOKEN = "CSP_ACCESS_TOKEN"
DISABLE_OAUTH_LOGIN = "DISABLE_OAUTH_LOGIN"
Team = "TEAM"


class OauthPluginConfiguration:
    def __init__(
        self,
        config: Configuration,
    ):
        self.__config = config

    def team(self):
        return self.__config.get_value(Team)

    def team_client_id(self):
        return self.__config.get_value(TEAM_CLIENT_ID)

    def team_client_secret(self):
        return self.__config.get_value(TEAM_CLIENT_SECRET)

    def control_service_rest_api_url(self):
        return self.__config.get_value(CONTROL_SERVICE_REST_API_URL)

    def api_token_authorization_url(self):
        return self.__config.get_value(API_TOKEN_AUTHORIZATION_URL)

    def team_oauth_authorize_url(self):
        return self.__config.get_value(TEAM_OAUTH_AUTHORIZE_URL)

    def csp_access_token(self):
        return self.__config.get_value(CSP_ACCESS_TOKEN)

    def disable_oauth_plugin(self):
        return self.__config.get_value(DISABLE_OAUTH_LOGIN)


def add_definitions(config_builder: ConfigurationBuilder) -> None:
    config_builder.add(
        key=DISABLE_OAUTH_LOGIN,
        default_value=False,
        description="To enable/disable oauth login.",
    )
