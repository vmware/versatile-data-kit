# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Optional

from requests.auth import AuthBase
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.control.auth.auth import Authentication
from taurus.vdk.control.auth.login_types import LoginTypes
from taurus.vdk.control_service_properties import Authenticator
from taurus.vdk.control_service_properties import ControlPlanePropertiesServiceClient
from taurus.vdk.control_service_properties import NoneAuthenticator
from taurus.vdk.core.config import ConfigurationBuilder

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
    conf = context.core_context.configuration
    auth = NoneAuthenticator()
    # TODO: it would better to centralize authentication (e.g AuthFactory)
    # since different components would need it.
    if conf.get_value(PROPERTIES_API_TOKEN):
        log.info("PROPERTIES_API_TOKEN is set - we will use API Token authentication")
        auth = ApiTokenAuthenticator(
            conf.get_required_value(PROPERTIES_API_TOKEN_AUTHORIZATION_URL),
            conf.get_value(PROPERTIES_API_TOKEN),
        )
    else:
        log.info("Properties API is configured without authentication")
    url = conf.get_value(PROPERTIES_API_URL)
    if url:
        team = conf.get_value("team")
        log.debug(f"url: {url}; team: {team}")
        context.properties.set_properties_factory_method(
            "default", lambda: ControlPlanePropertiesServiceClient(url, team, auth)
        )
    else:
        log.warning(
            "Plugin control service properties is installed "
            "but required configuration (PROPERTIES_API_URL) is not passed."
            "Control Service based properties will not be setup."
        )
