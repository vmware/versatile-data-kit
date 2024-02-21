# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json

from click.testing import Result
from vdk.plugin.data_sources import plugin_entry
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_sources_command_list():
    runner = CliEntryBasedTestRunner(plugin_entry)

    result: Result = runner.invoke(["data-sources", "--list", "-o", "json"])

    cli_assert_equal(0, result)
    assert json.loads(result.stdout) == [
        {
            "description": "Configuration for Auto generated data source",
            "name": "auto-generated-data",
        }
    ]


def test_sources_command_config():
    runner = CliEntryBasedTestRunner(plugin_entry)

    result: Result = runner.invoke(
        ["data-sources", "--config", "auto-generated-data", "-o", "json"]
    )

    cli_assert_equal(0, result)
    assert len(json.loads(result.stdout)) == 3
