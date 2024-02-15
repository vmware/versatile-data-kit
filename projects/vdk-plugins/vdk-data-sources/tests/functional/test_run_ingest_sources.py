# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from click.testing import Result
from vdk.plugin.data_sources import plugin_entry
from vdk.plugin.data_sources.auto_generated import AutoGeneratedDataSource
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


def test_run_ingest_sources():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin, plugin_entry)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-sources-job")]
    )

    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0


def test_run_ingest_data_flow_sources():
    a = AutoGeneratedDataSource
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin, plugin_entry)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-data-flow-job")]
    )

    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0


def test_run_ingest_data_flow_sources_toml():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin, plugin_entry)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-data-flow-toml-job")]
    )

    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0


def test_run_ingest_data_flow_with_map_function():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin, plugin_entry)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-data-flow-map-func-job")]
    )

    cli_assert_equal(0, result)

    assert ingest_plugin.payloads[0].payload == [
        {"id": 1, "name": "Stream_0_Name_0", "new_column": "new_column", "stream": 0},
        {"id": 2, "name": "Stream_0_Name_1", "new_column": "new_column", "stream": 0},
    ]


def test_run_ingest_sources_error_no_such_method():
    runner = CliEntryBasedTestRunner(plugin_entry)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-sources-job")]
    )

    cli_assert_equal(1, result)
