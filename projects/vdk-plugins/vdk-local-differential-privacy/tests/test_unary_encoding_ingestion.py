# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import math
import os
from typing import List
from unittest import mock

from click.testing import Result
from vdk.plugin.local_differential_privacy import differential_privacy_plugin
from vdk.plugin.local_differential_privacy.differential_private_unary_encoding import (
    DifferentialPrivateUnaryEncoding,
)
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


def ingest_data() -> List[int]:
    # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a way to simulate vdk command
    # and mock large parts of it - e.g passed our own plugins
    destination_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(differential_privacy_plugin, destination_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("unary-encoding")]
    )
    cli_assert_equal(0, result)

    actual_payload = destination_plugin.payloads[0].payload
    aggregated_results = DifferentialPrivateUnaryEncoding(0.75, 0.25).aggregate(
        [a["customer_os"] for a in actual_payload]
    )
    assert aggregated_results[0] < aggregated_results[1] - 20
    assert aggregated_results[2] < aggregated_results[1] - 20
    assert aggregated_results[3] < aggregated_results[1] - 20

    assert abs(aggregated_results[0] - aggregated_results[2]) < 20
    assert abs(aggregated_results[0] < aggregated_results[3]) < 20
    return aggregated_results


@mock.patch.dict(
    os.environ,
    {
        "VDK_INGEST_METHOD_DEFAULT": "memory",
        "VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "unary_encoding_differential_privacy",
        "VDK_DIFFERENTIAL_PRIVACY_UNARY_ENCODING_FIELDS": '{"sample_entity": {"customer_os":["MAC","WINDOWS","LINUX","JAILBROKEN_WINDOWS"]}}',
    },
)
def test_random_sampling_ingestion():
    aggregated_results_1 = ingest_data()
    aggregated_results_2 = ingest_data()
    aggregated_results_3 = ingest_data()

    # assert that there is randomness in the results, that we aren't producing the same result everytime
    assert (
        aggregated_results_1 != aggregated_results_2
        or aggregated_results_1 != aggregated_results_3
    )
