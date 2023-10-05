# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Functional test aiming at verifying that payload is verified
"""
import logging

from click.testing import Result
from vdk.plugin.test_utils.util_funcs import cli_assert
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


log = logging.getLogger(__name__)


def test_payload_verification_none():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin)

    # Use a sample data job, in which bad payload None is passed to
    # ingestion method call, thus causing a User Error to be raised.
    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("test-ingest-bad-payload-job"),
            "--arguments",
            '{"payload": "None"}',
        ]
    )

    cli_assert_equal(1, result)
    cli_assert(
        "Payload given to ingestion method should not be empty." in result.stdout,
        result,
    )


def test_payload_verification_bad_type():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin)

    # Use a sample data job, in which bad payload type string is passed to
    # ingestion method call, thus causing a User Error to be raised.
    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("test-ingest-bad-payload-job"),
            "--arguments",
            '{"payload": "wrong_type_string"}',
        ]
    )

    cli_assert_equal(1, result)
    cli_assert("InvalidPayloadTypeIngestionException" in result.stdout, result)


def test_payload_verification_unserializable():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin)

    # Use a sample data job, in which unserializable payload is passed to
    # ingestion method call, thus causing a User Error to be raised.
    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("test-ingest-bad-payload-job"),
            "--arguments",
            '{"payload": "date"}',
        ]
    )

    cli_assert_equal(1, result)
    cli_assert("Payload is not json serializable" in result.stdout, result)
