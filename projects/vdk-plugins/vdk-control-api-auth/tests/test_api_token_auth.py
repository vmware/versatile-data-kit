# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from test_core_auth import allow_oauthlib_insecure_transport
from test_core_auth import get_json_response_mock
from vdk.plugin.control_api_auth.auth_exception import VDKInvalidAuthParamError
from vdk.plugin.control_api_auth.authentication import Authentication


def test_api_token_success_authentication(httpserver: PluginHTTPServer):
    allow_oauthlib_insecure_transport()
    httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())

    auth = Authentication(
        token="apitoken",
        authorization_url=httpserver.url_for("/foo"),
        auth_type="api-token",
    )
    auth.authenticate()

    assert auth.read_access_token() == "axczfe12casASDCz"


def test_api_token_no_auth_url():
    auth = Authentication(token="apitoken", auth_type="api-token")

    with pytest.raises(VDKInvalidAuthParamError) as exc_info:
        auth.authenticate()

    raised_exception = exc_info.value
    assert "auth_url was not specified" in raised_exception.message


def test_api_token_no_auth_type_specified(httpserver: PluginHTTPServer):
    httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())
    auth = Authentication(
        token="apitoken", authorization_url=httpserver.url_for("/foo")
    )

    with pytest.raises(VDKInvalidAuthParamError) as exc_info:
        auth.authenticate()
    raised_exception = exc_info.value

    assert "auth_type was not specified" in raised_exception.message
