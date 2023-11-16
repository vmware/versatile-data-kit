# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from click.testing import Result
from vdk.plugin.data_sources import plugin_entry as data_sources_plugin_entry
from vdk.plugin.notebook import notebook_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


def test_ingest_vdkingest():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(
        ingest_plugin, data_sources_plugin_entry, notebook_plugin
    )

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-data-flow-job")]
    )

    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0
