# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import patch

import pytest
import snowflake
from vdk.plugin.snowflake.snowflake_connection import SnowflakeConnection


@pytest.fixture
def mock_connect(monkeypatch):
    def mock_connection(*args, **kwargs):
        if "account" in kwargs:
            if kwargs.get("account") != "localhost":
                raise Exception("The account provided doesn't exist!")
        else:
            return True

    monkeypatch.setattr(snowflake.connector, "connect", mock_connection)


def test_snowflake_connection_exception(mock_connect):
    with pytest.raises(Exception):
        conn = SnowflakeConnection(
            account="wrong_account",
            user="testuser",
            password="testpassword",
            warehouse=None,
            database=None,
            schema=None,
        )
        conn._connect()
