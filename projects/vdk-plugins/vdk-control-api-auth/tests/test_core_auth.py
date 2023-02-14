# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
This script contains test cases, verifying the core authentication components
of the plugin, like authentication cache, configurations, etc.
"""
import json
import os
from time import time
from unittest.mock import patch

from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.plugin.control_api_auth.auth_config import InMemAuthConfiguration
from vdk.plugin.control_api_auth.base_auth import AuthenticationCache
from vdk.plugin.control_api_auth.base_auth import AuthenticationCacheSerDe
from vdk.plugin.control_api_auth.base_auth import BaseAuth


def test_auth_cache_serialization_deserialization():
    cache = AuthenticationCache()
    cache_data = AuthenticationCacheSerDe.serialize(cache)
    serde_cache = AuthenticationCacheSerDe.deserialize(cache_data)
    assert cache == serde_cache


def test_auth_cache_backwards_compatibility_obsolete_keys():
    auth = AuthenticationCache("a", "r", "t")
    data_with_obsolete_keys = auth.__dict__
    data_with_obsolete_keys["obsolete_key"] = "value"
    cache_data = json.dumps(data_with_obsolete_keys)
    cache = AuthenticationCacheSerDe.deserialize(cache_data)
    assert cache.access_token == auth.access_token
    assert cache.refresh_token == auth.refresh_token


def test_auth_cache_backwards_compatibility_missing_keys():
    data_with_missing_keys = dict(refresh_token="value")
    cache_data = json.dumps(data_with_missing_keys)
    cache = AuthenticationCacheSerDe.deserialize(cache_data)
    assert cache.refresh_token == "value"
    assert cache.access_token is None


# The Following tests use the AuthConfigFolder to test configuration storage
# ==========================================================================
def test_auth_updates():
    with patch("vdk.plugin.control_api_auth.auth_config.AuthConfigFolder") as mock_conf:
        # after login cache is populated with auth uri and refresh token
        test_cache = AuthenticationCache()
        mock_conf.read_credentials.return_value = AuthenticationCacheSerDe.serialize(
            test_cache
        )
        auth = BaseAuth(mock_conf)
        auth.update_refresh_token("refresh")
        auth.update_access_token("access")
        auth.update_oauth2_authorization_url("http://uri")

        mock_conf.save_credentials.assert_called_with(
            '{"authorization_url": "http://uri", "refresh_token": "refresh", '
            '"access_token": "access", "access_token_expiration_time": 0, '
            '"client_id": null, "client_secret": null, '
            '"api_token": null, "api_token_authorization_url": null, "auth_type": null}'
        )


def test_auth_acquire_token(httpserver: PluginHTTPServer):
    allow_oauthlib_insecure_transport()
    with patch("vdk.plugin.control_api_auth.auth_config.AuthConfigFolder") as mock_conf:
        httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())

        test_cache = AuthenticationCache(
            api_token_authorization_url=httpserver.url_for("/foo"), api_token="refresh"
        )
        # after login cache is populated with auth uri and refresh token
        mock_conf.read_credentials.return_value = AuthenticationCacheSerDe.serialize(
            test_cache
        )

        auth = BaseAuth(mock_conf)
        auth.update_auth_type("api-token")
        auth.acquire_and_cache_access_token()

        saved_auth = AuthenticationCacheSerDe.deserialize(
            mock_conf.save_credentials.call_args[0][0]
        )
        assert saved_auth.access_token == "axczfe12casASDCz"
        assert saved_auth.access_token_expiration_time > time()


def test_auth_read_access_token_expired(httpserver: PluginHTTPServer):
    allow_oauthlib_insecure_transport()
    with patch("vdk.plugin.control_api_auth.auth_config.AuthConfigFolder") as mock_conf:
        httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())

        test_cache = AuthenticationCache(
            api_token_authorization_url=httpserver.url_for("/foo"),
            api_token="refresh",
            access_token="expired-token",
            access_token_expiration_time=time(),
        )
        # after login cache is populated with auth uri and refresh token
        mock_conf.read_credentials.return_value = AuthenticationCacheSerDe.serialize(
            test_cache
        )

        auth = BaseAuth(mock_conf)
        auth.update_auth_type("api-token")
        auth.read_access_token()

        saved_auth = AuthenticationCacheSerDe.deserialize(
            mock_conf.save_credentials.call_args[0][0]
        )
        # verify it is access token is changed:
        assert saved_auth.access_token == "axczfe12casASDCz"


def test_auth_read_access_token():
    with patch("vdk.plugin.control_api_auth.auth_config.AuthConfigFolder") as mock_conf:
        test_cache = AuthenticationCache(
            "http://foo", "refresh", "access-token", time() + 200
        )
        # after login cache is populated with auth uri and refresh token
        mock_conf.read_credentials.return_value = AuthenticationCacheSerDe.serialize(
            test_cache
        )

        auth = BaseAuth(mock_conf)

        assert auth.read_access_token() == "access-token"


# ============================================================================


# The Following tests use the InMemAuthConfiguration to test configuration
# storage
# ==========================================================================
def test_auth_updates_in_memory():
    # after login cache is populated with auth uri and refresh token
    in_mem_conf = InMemAuthConfiguration()
    auth = BaseAuth(in_mem_conf)
    auth.update_refresh_token("refresh")
    auth.update_access_token("access")
    auth.update_oauth2_authorization_url("http://uri")

    result = '{"authorization_url": "http://uri", "refresh_token": "refresh", "access_token": "access", "access_token_expiration_time": 0, "client_id": null, "client_secret": null, "api_token": null, "api_token_authorization_url": null, "auth_type": null}'

    assert in_mem_conf.read_credentials() == result


def test_auth_acquire_token_in_memory(httpserver: PluginHTTPServer):
    allow_oauthlib_insecure_transport()
    httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())
    in_mem_conf = InMemAuthConfiguration()

    auth = BaseAuth(conf=in_mem_conf)

    auth.update_auth_type("api-token")
    auth.update_api_token_authorization_url(httpserver.url_for("/foo"))
    auth.update_api_token("refresh")

    auth.acquire_and_cache_access_token()

    result = json.loads(in_mem_conf.read_credentials())
    assert result.get("access_token") == "axczfe12casASDCz"
    assert result.get("access_token_expiration_time") > time()


def test_auth_read_access_token_expired_in_memory(httpserver: PluginHTTPServer):
    allow_oauthlib_insecure_transport()
    httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())

    test_cache = AuthenticationCache(
        api_token_authorization_url=httpserver.url_for("/foo"),
        api_token="refresh",
        access_token="expired-token",
        access_token_expiration_time=time(),
    )
    in_mem_conf = InMemAuthConfiguration()
    in_mem_conf.save_credentials(AuthenticationCacheSerDe.serialize(test_cache))

    auth = BaseAuth(in_mem_conf)
    auth.update_auth_type("api-token")
    auth.read_access_token()

    saved_auth = json.loads(in_mem_conf.read_credentials())
    # verify it is access token is changed:
    assert saved_auth.get("access_token") == "axczfe12casASDCz"


def test_auth_read_access_token_in_memory():
    test_cache = AuthenticationCache(
        "http://foo", "refresh", "access-token", time() + 200
    )
    in_mem_conf = InMemAuthConfiguration()
    in_mem_conf.save_credentials(AuthenticationCacheSerDe.serialize(test_cache))

    auth = BaseAuth(in_mem_conf)

    assert auth.read_access_token() == "access-token"


# ============================================================================


def get_json_response_mock():
    json_response_mock = {
        "id_token": "",
        "token_type": "bearer",
        "expires_in": 1799,
        "scope": "csp:support_user",
        "access_token": "axczfe12casASDCz",
        "refresh_token": "refresh",
    }
    return json_response_mock


def allow_oauthlib_insecure_transport():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
