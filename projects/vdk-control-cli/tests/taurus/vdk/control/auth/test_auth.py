# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import time
from unittest.mock import patch

from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from taurus.vdk import test_utils
from taurus.vdk.control.auth.auth import Authentication
from taurus.vdk.control.auth.auth import AuthenticationCache
from taurus.vdk.control.auth.auth import AuthenticationCacheSerDe
from taurus.vdk.control.configuration.vdk_config import VDKConfigFolder


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


def test_auth_updates():
    with patch(
        "taurus.vdk.control.configuration.vdk_config.VDKConfigFolder"
    ) as mock_conf:
        # after login cache is populated with auth uri and refresh token
        test_cache = AuthenticationCache()
        mock_conf.read_credentials.return_value = AuthenticationCacheSerDe.serialize(
            test_cache
        )
        auth = Authentication(mock_conf)
        auth.update_refresh_token("refresh")
        auth.update_access_token("access")
        auth.update_oauth2_authorization_url("http://uri")

        mock_conf.save_credentials.assert_called_with(
            '{"authorization_url": "http://uri", "refresh_token": "refresh", '
            '"access_token": "access", "access_token_expiration_time": 0, '
            '"client_id": "not-used", "client_secret": "not-used", '
            '"api_token": null, "api_token_authorization_url": null, "auth_type": null}'
        )


def test_auth_acquire_token(httpserver: PluginHTTPServer):
    test_utils.allow_oauthlib_insecure_transport()
    with patch(
        "taurus.vdk.control.configuration.vdk_config.VDKConfigFolder"
    ) as mock_conf:
        httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())

        test_cache = AuthenticationCache(
            api_token_authorization_url=httpserver.url_for("/foo"), api_token="refresh"
        )
        # after login cache is populated with auth uri and refresh token
        mock_conf.read_credentials.return_value = AuthenticationCacheSerDe.serialize(
            test_cache
        )

        auth = Authentication(mock_conf)
        auth.update_auth_type("api-token")
        auth.acquire_and_cache_access_token()

        saved_auth = AuthenticationCacheSerDe.deserialize(
            mock_conf.save_credentials.call_args[0][0]
        )
        assert saved_auth.access_token == "axczfe12casASDCz"
        assert saved_auth.access_token_expiration_time > time.time()


def test_auth_read_access_token_expired(httpserver: PluginHTTPServer):
    test_utils.allow_oauthlib_insecure_transport()
    with patch(
        "taurus.vdk.control.configuration.vdk_config.VDKConfigFolder"
    ) as mock_conf:
        httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())

        test_cache = AuthenticationCache(
            api_token_authorization_url=httpserver.url_for("/foo"),
            api_token="refresh",
            access_token="expired-token",
            access_token_expiration_time=time.time(),
        )
        # after login cache is populated with auth uri and refresh token
        mock_conf.read_credentials.return_value = AuthenticationCacheSerDe.serialize(
            test_cache
        )

        auth = Authentication(mock_conf)
        auth.update_auth_type("api-token")
        auth.read_access_token()

        saved_auth = AuthenticationCacheSerDe.deserialize(
            mock_conf.save_credentials.call_args[0][0]
        )
        # verify it is access token is changed:
        assert saved_auth.access_token == "axczfe12casASDCz"


def test_auth_read_access_token_credentials(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    test_utils.allow_oauthlib_insecure_transport()
    mock_conf = VDKConfigFolder(base_dir=tmpdir)
    httpserver.expect_request("/foo").respond_with_json(get_json_response_mock())

    auth = Authentication(mock_conf)
    auth.update_oauth2_authorization_url(httpserver.url_for("/foo"))
    auth.update_client_id("id")
    auth.update_refresh_token("refresh")
    auth.update_auth_type("credentials")

    auth.acquire_and_cache_access_token()

    saved_auth = AuthenticationCacheSerDe.deserialize(mock_conf.read_credentials())
    # verify it is access token is changed:
    assert saved_auth.access_token == "axczfe12casASDCz"
    assert saved_auth.client_id == "id"
    assert saved_auth.auth_type == "credentials"
    assert saved_auth.authorization_url == httpserver.url_for("/foo")


def test_auth_read_access_token():
    with patch(
        "taurus.vdk.control.configuration.vdk_config.VDKConfigFolder"
    ) as mock_conf:
        test_cache = AuthenticationCache(
            "http://foo", "refresh", "access-token", time.time() + 200
        )
        # after login cache is populated with auth uri and refresh token
        mock_conf.read_credentials.return_value = AuthenticationCacheSerDe.serialize(
            test_cache
        )

        auth = Authentication(mock_conf)

        assert auth.read_access_token() == "access-token"


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
