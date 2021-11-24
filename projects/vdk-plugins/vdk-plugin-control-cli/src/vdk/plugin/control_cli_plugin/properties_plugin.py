# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Optional

from requests.auth import AuthBase
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.control.auth.auth import Authentication
from vdk.internal.control.auth.login_types import LoginTypes
from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.control_cli_plugin.control_service_configuration import (
    ControlServiceConfiguration,
)
from vdk.plugin.control_cli_plugin.control_service_properties import Authenticator
from vdk.plugin.control_cli_plugin.control_service_properties import (
    ControlPlanePropertiesServiceClient,
)
from vdk.plugin.control_cli_plugin.control_service_properties import NoneAuthenticator
from vdk.plugin.control_cli_plugin.control_service_properties_client import (
    ControlServicePropertiesServiceClient,
)

log = logging.getLogger(__name__)


class BearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


class ApiTokenAuthenticator(Authenticator):
    def __init__(self, api_token_authorization_url: str, api_token: str):
        self.__api_token_authorization_url = api_token_authorization_url
        self.__api_token = api_token

    def authenticate(self) -> Optional[AuthBase]:
        auth = Authentication()
        auth.update_api_token_authorization_url(self.__api_token_authorization_url)
        auth.update_api_token(self.__api_token)
        auth.update_auth_type(LoginTypes.API_TOKEN.value)
        auth.acquire_and_cache_access_token()

        return BearerAuth(auth.read_access_token())

    def get_authentication_instructions(self) -> str:
        msg = (
            "Please specify following configuration to authenticate: "
            "API_TOKEN_AUTHORIZATION_URL must be set correctly and will be used to exachange api token for access "
            "token."
            "API_TOKEN must be correct and valid - e.g make sure it has not expired."
        )
        return msg


PROPERTIES_API_TOKEN_AUTHORIZATION_URL = (
    "PROPERTIES_API_TOKEN_AUTHORIZATION_URL"  # nosec
)
PROPERTIES_API_TOKEN = "PROPERTIES_API_TOKEN"  # nosec
PROPERTIES_API_URL = "PROPERTIES_API_URL"


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    # TODO: can we levarage vdk-control-cli a bit more ?
    """
    Here we define what configuration settings are needed for trino with reasonable defaults
    """
    config_builder.add(
        key=PROPERTIES_API_TOKEN_AUTHORIZATION_URL,
        default_value=None,
        description="The Authorization URL which will be used to exchange api token for access token and"
        "authenticate to Control Service Properties API.",
    )
    config_builder.add(
        key=PROPERTIES_API_TOKEN,
        default_value=None,
        description="The api token. It will be exchange for access token "
        "in order to authenticate to Control Service Properties API .",
    )
    config_builder.add(
        key=PROPERTIES_API_URL,
        default_value=None,
        description="The api token. It will be exchange for access token "
        "in order to authenticate to Control Service Properties API."
        "It must contain {team_name} and {job_name} for example 'http://server/foo/{team_name}/bar/"
        "{job_name}'",
    )


@hookimpl
def initialize_job(context: JobContext) -> None:
    conf = ControlServiceConfiguration(context.core_context.configuration)
    url = conf.control_service_rest_api_url()
    if url:
        log.info("Initialize Control Service based Properties client implementation.")
        context.properties.set_properties_factory_method(
            "default", lambda: ControlServicePropertiesServiceClient(url)
        )
        context.properties.set_properties_factory_method(
            "control-service", lambda: ControlServicePropertiesServiceClient(url)
        )
    else:
        log.info(
            "Control Service REST API URL is not configured. Will not initialize Control Service based Properties client implementation."
        )
