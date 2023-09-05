# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock
from unittest.mock import MagicMock
from urllib.parse import parse_qs
from urllib.parse import urlparse

from tornado import httputil
from tornado.web import Application
from vdk.plugin.control_api_auth.base_auth import BaseAuth
from vdk_jupyterlab_extension.handlers import OAuth2Handler


def test_fix_redirect_uri():
    assert (
        OAuth2Handler._fix_localhost("http://localhost?foo=bar") == "http://127.0.0.1"
    )
    assert (
        OAuth2Handler._fix_localhost("http://localhost:8888?foo=bar")
        == "http://127.0.0.1:8888"
    )
    assert (
        OAuth2Handler._fix_localhost("http://something?foo=bar") == "http://something"
    )
    assert (
        OAuth2Handler._fix_localhost("http://something:9999?foo=bar")
        == "http://something:9999"
    )
    assert (
        OAuth2Handler._fix_localhost("http://something:9999") == "http://something:9999"
    )


import json
import httpretty
import pytest
from vdk_jupyterlab_extension import VdkJupyterConfig


@pytest.fixture(scope="module")
def vdk_config():
    return VdkJupyterConfig(
        oauth2_authorization_url="https://example.com/auth",
        oauth2_token_url="https://example.com/token",
        oauth2_client_id="sample_client_id",
        oauth2_redirect_url="http://my.app.com/redirect",
    )


@pytest.fixture
def oauth2_handler(vdk_config):
    request = httputil.HTTPServerRequest(
        uri="http://my.app.com/login", method="GET", connection=MagicMock()
    )
    handler = OAuth2Handler(Application(), request, vdk_config=vdk_config)
    handler.finish = MagicMock()
    return handler


@httpretty.activate
def test_get_without_code(oauth2_handler):
    # Arrange
    httpretty.register_uri(
        httpretty.GET,
        "https://example.com/auth",
        body="redirect_to_auth_server",
    )

    oauth2_handler.request.arguments = {}

    # Act
    oauth2_handler.get()

    # Assert
    mock_finish: MagicMock = oauth2_handler.finish

    auth_url = urlparse(mock_finish.call_args[0][0])
    assert auth_url.netloc == "example.com"
    assert auth_url.path == "/auth"
    assert auth_url.scheme == "https"

    query_params = parse_qs(auth_url.query)
    assert query_params.get("response_type") == ["code"]
    assert query_params.get("client_id") == ["sample_client_id"]
    assert query_params.get("code_challenge")


@httpretty.activate
def test_get_with_code(oauth2_handler: OAuth2Handler, tmpdir):
    with mock.patch.dict(
        os.environ,
        {"VDK_BASE_CONFIG_FOLDER": str(tmpdir)},
    ):
        # Arrange
        oauth2_handler.application.settings["code_verifier"] = "random"
        mock_token_response = {
            "access_token": "sample_token",
            "expires_in": 3600,
        }
        httpretty.register_uri(
            httpretty.POST,
            "https://example.com/token",
            body=json.dumps(mock_token_response),
        )

        # Mock the request to contain a code
        oauth2_handler.request.arguments = {"code": ["sample_code"]}

        # Act
        oauth2_handler.get()

        # Assert
        # The access token must be safely stored in VDK auth storage
        auth = BaseAuth()
        assert auth.read_access_token() == "sample_token"
