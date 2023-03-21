# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

import numpy as np
from click.testing import Result
from vdk.plugin.local_differential_privacy import differential_privacy_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


def ingest_data():
    # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a way to simulate vdk command
    # and mock large parts of it - e.g passed our own plugins
    destination_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(differential_privacy_plugin, destination_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("random-sampling")]
    )
    cli_assert_equal(0, result)

    payload = destination_plugin.payloads[0].payload
    count_of_true = np.count_nonzero([a["sensitive_key"] for a in payload])
    count_of_false = len(payload) - count_of_true

    assert list(payload[0].keys()) == ["str_key", "sensitive_key"]
    assert payload[0]["str_key"] == "str"
    assert count_of_false > count_of_true + 20
    return payload


@mock.patch.dict(
    os.environ,
    {
        "VDK_INGEST_METHOD_DEFAULT": "memory",
        "VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "random_response_differential_privacy",
        "VDK_DIFFERENTIAL_PRIVACY_RANDOMIZED_RESPONSE_FIELDS": '{"sample_entity": ["sensitive_key"]}',
    },
)
def test_random_sampling_ingestion():
    payload_1 = ingest_data()
    payload_2 = ingest_data()
    payload_3 = ingest_data()

    # assert that there is randomness in the results, that we aren't producing the same result everytime
    assert [a["sensitive_key"] for a in payload_1] != [
        a["sensitive_key"] for a in payload_2
    ] or [a["sensitive_key"] for a in payload_1] != [
        a["sensitive_key"] for a in payload_3
    ]
