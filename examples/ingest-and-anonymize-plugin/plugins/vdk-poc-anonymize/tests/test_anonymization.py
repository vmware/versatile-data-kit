# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from vdk.plugin.anonymize import anonymization_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


@mock.patch.dict(
    os.environ,
    {
        "VDK_INGEST_METHOD_DEFAULT": "memory",
        "VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "anonymize",
        "VDK_ANONYMIZATION_FIELDS": '{"sample_entity": ["sensitive_key"]}',
    },
)
def test_anonymization_ingestion():
    # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a way to simulate vdk command
    # and mock large parts of it - e.g passed our own plugins
    destination_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(anonymization_plugin, destination_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest-job")]
    )
    cli_assert_equal(0, result)

    actual_payload = destination_plugin.payloads[0].payload
    expected_payload = [
        {
            "str_key": "str",
            "sensitive_key": "a46e1b9d0e3467d52e2dfc2e902f6c3f8c3529dde2df62652a25b4d4aebae5af",
        },
        {
            "str_key": "str",
            "sensitive_key": "d64e011391b12310cb932f47f9464d53367e5378e2d6900aa56495fba238d65c",
        },
    ]
    assert actual_payload == expected_payload
