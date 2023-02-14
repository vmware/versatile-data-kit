# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from test_core_auth import allow_oauthlib_insecure_transport
from test_core_auth import get_json_response_mock
from vdk.plugin.control_api_auth.auth_exception import VDKInvalidAuthParamError
from vdk.plugin.control_api_auth.auth_exception import VDKLoginFailedError
from vdk.plugin.control_api_auth.authentication import Authentication
from vdk.plugin.control_api_auth.autorization_code_auth import LoginHandler
from vdk.plugin.control_api_auth.autorization_code_auth import RedirectAuthentication
from vdk.plugin.control_api_auth.base_auth import BaseAuth
from vdk.plugin.control_api_auth.base_auth import InMemAuthConfiguration


def test_verify_redirect_url():
    allow_oauthlib_insecure_transport()
    in_mem_conf = InMemAuthConfiguration()
    auth = BaseAuth(in_mem_conf)

    auth = RedirectAuthentication(
        client_id="client-id",
        client_secret="client-secret",
        oauth2_discovery_url="http://discovery-url",
        oauth2_exchange_url="http://exchange-url",
        auth=auth,
        redirect_uri="http://127.0.0.1",
        redirect_uri_default_port=9999,
    )
    authorization_url = auth._create_authorization_redirect_url()
    assert (
        authorization_url[0]
        == "http://discovery-url?response_type=code&client_id=client-id&redirect_uri=http%3A%2F%2F127.0.0.1%3A9999&state=requested&prompt=login"
    )
    assert authorization_url[1] == "requested"


def test_login_handler_exceptions(httpserver: PluginHTTPServer):
    allow_oauthlib_insecure_transport()
    httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())
    in_mem_conf = InMemAuthConfiguration()
    auth = BaseAuth(in_mem_conf)

    handler = LoginHandler(
        client_id=None,
        client_secret=None,
        exchange_endpoint=httpserver.url_for("/foo"),
        redirect_uri=None,
        code_verifier=None,
        auth=auth,
    )

    with pytest.raises(VDKLoginFailedError) as exc_info:
        handler.login_with_authorization_code(
            path="http://test-url?code=test-auth-code&client_id=client-id&redirect_uri=http%3A%2F%2F127.0.0.1%3A9999&prompt=login"
        )
    raised_exception = exc_info.value
    assert "Failed to login." in raised_exception.message
    assert "Possibly the request was intercepted." in raised_exception.message

    with pytest.raises(VDKLoginFailedError) as exc_info2:
        handler.login_with_authorization_code(
            path="http://test-url?client_id=client-id&redirect_uri=http%3A%2F%2F127.0.0.1%3A9999&state=requested&prompt=login"
        )
    raised_exception2 = exc_info2.value
    assert "Authentication code is empty" in raised_exception2.message
    assert "The user failed to authenticate properly." in raised_exception2.message


def test_authorization_code_no_secret(httpserver: PluginHTTPServer):
    allow_oauthlib_insecure_transport()
    httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())

    auth = Authentication(
        token="apitoken",
        authorization_url=httpserver.url_for("/foo"),
        auth_type="credentials",
    )
    with pytest.raises(VDKInvalidAuthParamError) as exc_info:
        auth.authenticate()

    raised_exception = exc_info.value
    assert "Unable to log in." in raised_exception.message
    assert "Specify client_id and auth_discovery_url" in raised_exception.message
