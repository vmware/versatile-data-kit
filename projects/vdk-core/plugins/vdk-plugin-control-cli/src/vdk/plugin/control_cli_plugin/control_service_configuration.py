# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

API_TOKEN = "API_TOKEN"
API_TOKEN_AUTHORIZATION_URL = "API_TOKEN_AUTHORIZATION_URL"
CONTROL_SERVICE_REST_API_URL = "CONTROL_SERVICE_REST_API_URL"
CONTROL_SAMPLE_JOB_DIRECTORY = "CONTROL_SAMPLE_JOB_DIRECTORY"
CONTROL_HTTP_VERIFY_SSL = "CONTROL_HTTP_VERIFY_SSL"
CONTROL_HTTP_TOTAL_RETRIES = "CONTROL_HTTP_TOTAL_RETRIES"
CONTROL_HTTP_READ_RETRIES = "CONTROL_HTTP_READ_RETRIES"
CONTROL_HTTP_READ_TIMEOUT_SECONDS = "CONTROL_HTTP_READ_TIMEOUT_SECONDS"
CONTROL_HTTP_CONNECT_RETRIES = "CONTROL_HTTP_CONNECT_RETRIES"
CONTROL_HTTP_CONNECT_TIMEOUT_SECONDS = "CONTROL_HTTP_CONNECT_TIMEOUT_SECONDS"


class ControlServiceConfiguration:
    def __init__(self, config: Configuration) -> None:
        self.__config = config

    def api_token(self):
        return self.__config.get_value(API_TOKEN)

    def api_token_authorization_url(self):
        return self.__config.get_value(API_TOKEN_AUTHORIZATION_URL)

    def control_service_rest_api_url(self):
        return self.__config.get_value(CONTROL_SERVICE_REST_API_URL)

    def control_sample_job_directory(self):
        return self.__config.get_value(CONTROL_SAMPLE_JOB_DIRECTORY)

    def control_http_verify_ssl(self):
        return self.__config.get_value(CONTROL_HTTP_VERIFY_SSL)

    def control_http_total_retries(self):
        return self.__config.get_value(CONTROL_HTTP_TOTAL_RETRIES)

    def control_http_read_retries(self):
        return self.__config.get_value(CONTROL_HTTP_READ_RETRIES)

    def control_http_read_timeout_seconds(self):
        return self.__config.get_value(CONTROL_HTTP_READ_TIMEOUT_SECONDS)

    def control_http_connect_retries(self):
        return self.__config.get_value(CONTROL_HTTP_CONNECT_RETRIES)

    def control_http_connect_timeout_seconds(self):
        return self.__config.get_value(CONTROL_HTTP_CONNECT_TIMEOUT_SECONDS)


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=API_TOKEN,
        default_value=None,
        description="Default API Token to use if another authentication has not been used with vdk login.",
    )
    config_builder.add(
        key=API_TOKEN_AUTHORIZATION_URL,
        default_value=None,
        description="Location of the API Token OAuth2 provider. "
        "It is used to exchange api refresh token for access token. "
        "See https://tools.ietf.org/html/rfc6749#section-5.1"
        "It is used alongside API_TOKEN if vdk login has not been run.",
    )
    config_builder.add(
        key=CONTROL_SERVICE_REST_API_URL,
        default_value=None,
        description="The default base REST API URL. It looks like http://server (without path e.g. /data-jobs).",
    )
    config_builder.add(
        key=CONTROL_SAMPLE_JOB_DIRECTORY,
        default_value=None,
        description="Directory used to create sample job locally during vdk create --local operation. "
        "If not set it will use a predefined prepared one that should show basic sample job.",
    )
    config_builder.add(
        key=CONTROL_HTTP_VERIFY_SSL,
        default_value=True,
        description="Verify SSL certificate of Control Service Server.",
    )
    config_builder.add(
        key=CONTROL_HTTP_TOTAL_RETRIES,
        default_value=None,
        description="Total number of http retries to allow for Control Service API requests.",
    )
    config_builder.add(
        key=CONTROL_HTTP_READ_RETRIES,
        default_value=None,
        description="Total number of http retries to allow for Control Service API requests.",
    )
    config_builder.add(
        key=CONTROL_HTTP_CONNECT_RETRIES,
        default_value=None,
        description="How many connection-related errors to retry on against Control Service API Server."
        "These are errors raised before the request is sent to the remote server, "
        "which we assume has not triggered the server to process the request.",
    )
