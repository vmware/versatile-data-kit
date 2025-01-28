# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import patch

import pytest
from vdk.plugin.control_api_auth.auth_config import InMemoryCredentialsCache
from vdk.plugin.control_api_auth.authentication import Authentication


def test_get_authenticated_username_with_username():
    auth = Authentication(
        username="testuser", credentials_cache=InMemoryCredentialsCache()
    )
    assert auth.get_authenticated_username() == "testuser"


@patch("jwt.decode")
def test_get_authenticated_username_with_token_username(mock_jwt_decode):
    mock_jwt_decode.return_value = {"username": "testuser"}
    auth = Authentication(
        token="testtoken", credentials_cache=InMemoryCredentialsCache()
    )
    assert auth.get_authenticated_username() == "testuser"


@pytest.mark.parametrize("user_id_field", ["acct", "email", "preferred_username"])
@patch("jwt.decode")
def test_get_authenticated_username_with_token_other_fields(
    mock_jwt_decode, user_id_field
):
    mock_jwt_decode.return_value = {user_id_field: "testuser"}
    auth = Authentication(
        token="testtoken", credentials_cache=InMemoryCredentialsCache()
    )
    assert auth.get_authenticated_username() == "testuser"


@patch("jwt.decode")
def test_get_authenticated_username_with_token_no_user_id(mock_jwt_decode):
    mock_jwt_decode.return_value = {}
    auth = Authentication(
        token="testtoken", credentials_cache=InMemoryCredentialsCache()
    )
    assert auth.get_authenticated_username() is None


@patch("jwt.decode")
def test_get_authenticated_username_priority_order_kept(mock_jwt_decode):
    mock_jwt_decode.return_value = {"sub": "user_from_sub", "acct": "user_from_acct"}
    auth = Authentication(
        token="testtoken",
        credentials_cache=InMemoryCredentialsCache(),
        possible_jwt_user_keys=["user", "email", "sub", "acct"],
    )
    assert auth.get_authenticated_username() == "user_from_sub"


def test_get_authenticated_username_without_username_or_token():
    auth = Authentication(credentials_cache=InMemoryCredentialsCache())
    assert auth.get_authenticated_username() is None
