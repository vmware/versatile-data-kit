# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import os
from unittest import mock

import click
import pytest
from click.testing import Result
from pytest_httpserver import HTTPServer
from vdk.plugin.data_sources import plugin_entry as data_sources_plugin_entry
from vdk.plugin.singer import plugin_entry
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


@pytest.mark.skip
def test_run_ingest_gitlab_data_singer():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(
        ingest_plugin, plugin_entry, data_sources_plugin_entry
    )

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-singer-tap-job")]
    )

    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0
    payload = ingest_plugin.payloads[0]
    assert payload.destination_table
    assert len(payload.payload) > 0


def test_run_api_ingest(httpserver: HTTPServer, tmpdir):
    fake_data = simple_fake_json_data()
    nested_fake_data = nested_fake_json_data()

    api_url = httpserver.url_for("")
    httpserver.expect_request("/fake_data").respond_with_json(fake_data)
    httpserver.expect_request("/nested_fake_data").respond_with_json(nested_fake_data)

    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": str(tmpdir) + "vdk-sqlite.db",
        },
    ):
        runner = CliEntryBasedTestRunner(
            sqlite_plugin, plugin_entry, data_sources_plugin_entry
        )

        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("ingest-singer-tap-api-job"),
                "--arguments",
                json.dumps(dict(api_url=api_url)),
            ]
        )

        cli_assert_equal(0, result)

        check_result = query_table(runner, "some_data")
        assert json.loads(check_result.stdout) == fake_data

        check_result = query_table(runner, "some_nested_data")
        assert json.loads(check_result.stdout) == get_expected_nested_table_data()


def query_table(runner: CliEntryBasedTestRunner, table_name: str):
    check_result = runner.invoke(
        ["sql-query", "--output", "json", "--query", f"SELECT * FROM {table_name}"],
        runner=click.testing.CliRunner(
            mix_stderr=False
        ),  # TODO: replace when CliEntryBasedTestRunner add support for it
    )
    return check_result


def get_expected_nested_table_data():
    return [
        {
            "address_city": "Gwenborough",
            "address_geo_lat": "-37.3159",
            "address_geo_lng": "81.1496",
            "id": 1,
            "username": "Bret",
        },
        {
            "address_city": "Wisokyburgh",
            "address_geo_lat": "-43.9509",
            "address_geo_lng": "-34.4618",
            "id": 2,
            "username": "Antonette",
        },
        {
            "address_city": "McKenziehaven",
            "address_geo_lat": "-68.6102",
            "address_geo_lng": "-47.0653",
            "id": 3,
            "username": "Samantha",
        },
    ]


def nested_fake_json_data():
    data = [
        {
            "id": 1,
            "username": "Bret",
            "address": {
                "city": "Gwenborough",
                "geo": {"lat": "-37.3159", "lng": "81.1496"},
            },
        },
        {
            "id": 2,
            "username": "Antonette",
            "address": {
                "city": "Wisokyburgh",
                "geo": {"lat": "-43.9509", "lng": "-34.4618"},
            },
        },
        {
            "id": 3,
            "username": "Samantha",
            "address": {
                "city": "McKenziehaven",
                "geo": {"lat": "-68.6102", "lng": "-47.0653"},
            },
        },
    ]
    return data


def simple_fake_json_data():
    return [
        {
            "str_col": "str_data",
            "int_col": 11,
            "bool_col": True,
            # "float_col": 1.23, sqlite doesn't support Decimal
            "extra_col": None,
        },
        {
            "str_col": "str_data",
            "int_col": 11,
            "bool_col": True,
            # "float_col": 1.23, sqlite doesn't support Decimal
            "extra_col": 1,
        },
    ]
