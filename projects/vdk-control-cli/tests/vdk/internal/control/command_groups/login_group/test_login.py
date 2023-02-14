# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
from unittest.mock import patch
from urllib import parse

import requests
from click.testing import CliRunner
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal import test_utils
from vdk.internal.control.command_groups.login_group.login import login
from werkzeug import Request
from werkzeug import Response

# https://click.palletsprojects.com/en/7.x/testing/
# https://pytest-httpserver.readthedocs.io/en/latest/


def test_login(httpserver: PluginHTTPServer):
    test_utils.allow_oauthlib_insecure_transport()
    httpserver.expect_request("/foo").respond_with_json(
        test_utils.get_json_response_mock()
    )

    runner = CliRunner()
    result = runner.invoke(
        login, ["-t", "api-token", "-u", httpserver.url_for("/foo"), "-a", "NqxjAfax"]
    )

    test_utils.assert_click_status(result, 0)
    assert result.output == "Login Successful\n"


# TODO: testing error cases also return exit code 0 which should not be correct.


def test_login_credentials_manually(httpserver: PluginHTTPServer):
    with patch("webbrowser.open") as mock_browser:
        mock_browser.return_value = False

        test_utils.allow_oauthlib_insecure_transport()
        httpserver.expect_request("/exchange").respond_with_json(
            test_utils.get_json_response_mock()
        )
        runner = CliRunner()
        result = runner.invoke(
            login,
            [
                "-t",
                "credentials",
                "--oauth2-discovery-url",
                httpserver.url_for("/discovery"),
                "--oauth2-exchange-url",
                httpserver.url_for("/exchange"),
                "--client-id",
                "client_id",
                "--client-secret",
                "client_secret",
            ],
            input="http://127.0.0.1:1111/?code=my_auth_code&state=requested",
        )

        test_utils.assert_click_status(result, 0)


def _mock_browser_login(url):
    redirect_uri = parse.parse_qs(parse.urlparse(url).query)["redirect_uri"][0]
    try:
        # fire and forget - we do not care about the response
        requests.get(
            f"{redirect_uri}/?code=my-auth-code&state=requested", timeout=0.0000000001
        )
    except requests.exceptions.ReadTimeout:
        pass
    return True


def test_login_credentials_with_browser(httpserver: PluginHTTPServer):
    with patch("webbrowser.open") as mock_browser:
        test_utils.allow_oauthlib_insecure_transport()

        mock_browser.side_effect = _mock_browser_login

        httpserver.expect_request("/exchange").respond_with_json(
            test_utils.get_json_response_mock()
        )
        runner = CliRunner()
        result = runner.invoke(
            login,
            [
                "-t",
                "credentials",
                "--oauth2-discovery-url",
                httpserver.url_for("/discovery"),
                "--oauth2-exchange-url",
                httpserver.url_for("/exchange"),
                "--client-id",
                "client_id",
                "--client-secret",
                "client_secret",
            ],
        )

        test_utils.assert_click_status(result, 0)


def test_login_credentials_with_browser_as_native_app_auth(
    httpserver: PluginHTTPServer,
):
    with patch("webbrowser.open") as mock_browser:
        test_utils.allow_oauthlib_insecure_transport()

        mock_browser.side_effect = _mock_browser_login

        def exchange_response(req: Request):
            if "code_verifier" in req.get_data(as_text=True):
                response_data = json.dumps(
                    test_utils.get_json_response_mock(), indent=4
                )
                return Response(response_data, 200, None, None, "application/json")
            else:
                return Response("Missing code_verifier which is required by PKCE", 400)

        httpserver.expect_request("/exchange").respond_with_handler(exchange_response)
        runner = CliRunner()
        result = runner.invoke(
            login,
            [
                "-t",
                "credentials",
                "--oauth2-discovery-url",
                httpserver.url_for("/discovery"),
                "--oauth2-exchange-url",
                httpserver.url_for("/exchange"),
                "--client-id",
                "client_id",
                "--client-secret",
                "",
            ],
        )

        test_utils.assert_click_status(result, 0)


def test_login_credentials_exceptions(httpserver: PluginHTTPServer):
    with patch("webbrowser.open") as mock_browser:
        test_utils.allow_oauthlib_insecure_transport()

        mock_browser.side_effect = _mock_browser_login
        httpserver.expect_request("/exchange").respond_with_json(
            test_utils.get_json_response_mock()
        )

        runner = CliRunner()

        # Assert error message when no --oauth2-exchange-url provided.
        result = runner.invoke(
            login,
            [
                "-t",
                "credentials",
                "--oauth2-discovery-url",
                httpserver.url_for("/discovery"),
                "--client-id",
                "client_id",
                "--client-secret",
                "client_secret",
            ],
        )
        test_utils.assert_click_status(result, 1)
        assert (
            "requires arguments:, --client-secret, --client-id, --oauth2-exchange-url, --oauth2-discovery-url"
            in result.output
        )

        # Assert error message when no --oauth2-discovery-url provided.
        result = runner.invoke(
            login,
            [
                "-t",
                "credentials",
                "--oauth2-exchange-url",
                httpserver.url_for("/exchange"),
                "--client-id",
                "client_id",
                "--client-secret",
                "client_secret",
            ],
        )
        test_utils.assert_click_status(result, 1)
        assert (
            "requires arguments:, --client-secret, --client-id, --oauth2-exchange-url, --oauth2-discovery-url"
            in result.output
        )

        # Assert error message when no --client-id provided.
        result = runner.invoke(
            login,
            [
                "-t",
                "credentials",
                "--oauth2-discovery-url",
                httpserver.url_for("/discovery"),
                "--oauth2-exchange-url",
                httpserver.url_for("/exchange"),
                "--client-secret",
                "client_secret",
            ],
        )
        test_utils.assert_click_status(result, 1)
        assert (
            "requires arguments:, --client-secret, --client-id, --oauth2-exchange-url, --oauth2-discovery-url"
            in result.output
        )
