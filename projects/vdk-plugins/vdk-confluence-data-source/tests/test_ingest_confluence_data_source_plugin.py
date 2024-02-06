import os
import pathlib
from unittest import mock

from click.testing import Result
from vdk.plugin.confluence_data_source import plugin_entry
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.data_sources import plugin_entry as data_sources_plugin_entry

"""
This is a sample test file showing a recommended way to test new plugins.
A good way to test a new plugin is how it would be used in the command that it extends.
"""


def test_run_api_ingest(tmpdir):

    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin, data_sources_plugin_entry, plugin_entry)
    source_configuration = {}

    result: Result = runner.invoke(
        ["run",
         jobs_path_from_caller_directory("ingest-test-job"),
        "--arguments",
        json.dumps({"config": source_configuration})]
    )

    cli_assert_equal(0, result)

    assert ingest_plugin.payloads == get_expected_data()


def get_expected_data():
    return []