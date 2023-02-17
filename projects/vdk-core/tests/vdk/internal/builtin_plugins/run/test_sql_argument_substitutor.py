# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
from vdk.internal.builtin_plugins.run.sql_argument_substitutor import (
    SqlArgumentSubstitutor,
)


@pytest.fixture
def substitutor() -> SqlArgumentSubstitutor:
    properties = {"db": "history", "int": 5, "DB": "history_staging"}
    substitutor = SqlArgumentSubstitutor(properties)
    return substitutor


@pytest.mark.parametrize(
    "sql, expected_sql",
    (
        ("11{db}22", "11history22"),
        ("{DB}", "history_staging"),
        ("select * from history.bundle;", "select * from history.bundle;"),
        ("select * from {undefined};", "select * from {undefined};"),
        ("select * from {undefined}{db}{int};", "select * from {undefined}history5;"),
    ),
)
def test_sql_argument_substitutor_should_change_original_sql_length_after_substitution(
    substitutor, sql, expected_sql
):
    assert substitutor.substitute(sql) == expected_sql
