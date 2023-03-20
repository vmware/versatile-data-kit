# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from vdk.plugin.differential_privacy import differential_privacy_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


@mock.patch.dict(
    os.environ,
    {
        "VDK_INGEST_METHOD_DEFAULT": "memory",
        "VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "differential_privacy",
        "VDK_DIFFERENTIAL_PRIVACY_UNARY_ENCODING_FIELDS": '{"sample_entity": {"customer_os":["MAC","WINDOWS","LINUX","JAILBROKEN_WINDOWS"]}',
    },
)
def test_random_sampling_ingestion():
    # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a way to simulate vdk command
    # and mock large parts of it - e.g passed our own plugins
    destination_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(differential_privacy_plugin, destination_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-job")]
    )
    cli_assert_equal(0, result)

    actual_payload = destination_plugin.payloads[0].payload
