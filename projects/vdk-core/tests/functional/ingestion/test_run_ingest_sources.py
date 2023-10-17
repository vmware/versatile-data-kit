# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from typing import List
from typing import Optional
from unittest import mock

from click.testing import Result
from vdk.internal.builtin_plugins.ingestion.ingester_configuration import (
    INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND,
)
from vdk.plugin.test_utils.util_funcs import cli_assert
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


def test_run_ingest_sources():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-sources-job")]
    )

    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0


def test_run_ingest_sources_error_no_such_method():
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-sources-job")]
    )

    cli_assert_equal(1, result)
