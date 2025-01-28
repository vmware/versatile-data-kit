# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from click.testing import Result
from vdk.plugin.data_source_git import plugin_entry
from vdk.plugin.data_sources import plugin_entry as data_sources_plugin_entry
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


def test_run_ingest_git():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(
        ingest_plugin, data_sources_plugin_entry, plugin_entry
    )

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-git-job")]
    )

    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0
