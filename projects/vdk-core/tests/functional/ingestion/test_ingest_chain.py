# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Functional test aiming at verifying the end-to-end operation of the
ingestion plugins chaining functionality
"""
import logging
import os
from unittest import mock

from click.testing import Result
from vdk.plugin.test_utils.ingest_util_plugins import AddPayloadSizeAsColumn
from vdk.plugin.test_utils.ingest_util_plugins import ConvertPayloadValuesToString
from vdk.plugin.test_utils.ingest_util_plugins import DummyIngestionPlugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


log = logging.getLogger(__name__)


def get_shared_result_data():
    expected_object = dict(
        int_key=str(42),
        str_key="example_str",
        bool_key=str(True),
        float_key=str(1.23),
        nested=str(dict(key="value")),
        payload_size=163,
    )
    expected_rows_object = {"first": "two", "payload_size": 80, "second": "2"}

    return expected_object, expected_rows_object


# INGEST_PAYLOAD_PREPROCESS_SEQUENCE=""
@mock.patch.dict(
    os.environ,
    {"VDK_INGEST_METHOD_DEFAULT": "memory"},
)
def test_ingest_no_preprocessing():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("no-ingest-method-job")]
    )

    cli_assert_equal(0, result)

    expected_object = dict(
        int_key=42,
        str_key="example_str",
        bool_key=True,
        float_key=1.23,
        nested=dict(key="value"),
    )
    assert ingest_plugin.payloads[0].payload[0] == expected_object
    assert ingest_plugin.payloads[0].destination_table == "object_table"

    expected_rows_object = {"first": "two", "second": 2}
    assert ingest_plugin.payloads[1].payload[0] == expected_rows_object
    assert ingest_plugin.payloads[1].destination_table == "tabular_table"


# INGEST_PAYLOAD_PREPROCESS_SEQUENCE=A,B in job code method = C
@mock.patch.dict(
    os.environ,
    {"VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "convert-to-string," "add-payload-size"},
)
def test_chained_ingest_direct_method_passed():
    pre_ingest_plugin = ConvertPayloadValuesToString()
    payload_size_plugin = AddPayloadSizeAsColumn()
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(
        pre_ingest_plugin, payload_size_plugin, ingest_plugin
    )
    expected_object, expected_rows_object = get_shared_result_data()

    # Use a sample data job, in which `method` argument is passed to ingestion
    # method calls.
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("test-ingest-job")]
    )

    cli_assert_equal(0, result)

    assert ingest_plugin.payloads[0].payload[0] == expected_object
    assert ingest_plugin.payloads[0].destination_table == "object_table"

    assert ingest_plugin.payloads[1].payload[0] == expected_rows_object
    assert ingest_plugin.payloads[1].destination_table == "tabular_table"


# INGEST_PAYLOAD_PREPROCESS_SEQUENCE=A,B no ingest method specified
@mock.patch.dict(
    os.environ,
    {"VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "convert-to-string," "add-payload-size"},
)
def test_chained_ingest_no_method_passed():
    pre_ingest_plugin = ConvertPayloadValuesToString()
    payload_size_plugin = AddPayloadSizeAsColumn()
    runner = CliEntryBasedTestRunner(pre_ingest_plugin, payload_size_plugin)

    # Use a sample data job, in which `method` argument is not passed to
    # ingestion method calls, thus causing an User Error to be raised.
    # NOTE: pre-process plugins will not be invoked.
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("no-ingest-method-job")]
    )

    cli_assert_equal(1, result)
    assert "User Error" in result.stdout


# INGEST_PAYLOAD_PREPROCESS_SEQUENCE=A,B and VDK_INGEST_METHOD_DEFAULT=C
@mock.patch.dict(
    os.environ,
    {
        "VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "convert-to-string,"
        "add-payload-size",
        "VDK_INGEST_METHOD_DEFAULT": "memory",
    },
)
def test_chained_ingest_no_direct_method_passed():
    payload_to_string_plugin = ConvertPayloadValuesToString()
    payload_size_plugin = AddPayloadSizeAsColumn()
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(
        payload_to_string_plugin, payload_size_plugin, ingest_plugin
    )
    expected_object, expected_rows_object = get_shared_result_data()

    # Use a sample data job, in which `method` argument is not passed to
    # ingestion method calls.
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("no-ingest-method-job")]
    )

    cli_assert_equal(0, result)

    assert ingest_plugin.payloads[0].payload[0] == expected_object
    assert ingest_plugin.payloads[0].destination_table == "object_table"

    assert ingest_plugin.payloads[1].payload[0] == expected_rows_object
    assert ingest_plugin.payloads[1].destination_table == "tabular_table"


# INGEST_PAYLOAD_PREPROCESS_SEQUENCE=A,B and VDK_INGEST_METHOD_DEFAULT=C and
#    job code is D
@mock.patch.dict(
    os.environ,
    {
        "VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "convert-to-string,"
        "add-payload-size",
        "VDK_INGEST_METHOD_DEFAULT": "dummy-ingest",
    },
)
def test_chained_ingest_no_direct_method_passed():
    payload_to_string_plugin = ConvertPayloadValuesToString()
    payload_size_plugin = AddPayloadSizeAsColumn()
    dummy_ingest_plugin = DummyIngestionPlugin()
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(
        payload_to_string_plugin,
        payload_size_plugin,
        dummy_ingest_plugin,
        ingest_plugin,
    )
    expected_object, expected_rows_object = get_shared_result_data()

    # Use a sample data job, in which `method` argument is not passed to
    # ingestion method calls.
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("test-ingest-job")]
    )

    cli_assert_equal(0, result)

    assert ingest_plugin.payloads[0].payload[0] == expected_object
    assert ingest_plugin.payloads[0].destination_table == "object_table"

    assert ingest_plugin.payloads[1].payload[0] == expected_rows_object
    assert ingest_plugin.payloads[1].destination_table == "tabular_table"


# INGEST_PAYLOAD_PREPROCESS_SEQUENCE=A,B - A,B are used for pre-processing,
#    B is used for ingesting and post-processing.
# TODO: modify add-payload-size plugin to expose the result from post-ingestion
#  to verify post-processor operations
@mock.patch.dict(
    os.environ,
    {
        "VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "convert-to-string,"
        "add-payload-size",
        "VDK_INGEST_METHOD_DEFAULT": "add-payload-size",
        "VDK_INGEST_PAYLOAD_POSTPROCESS_SEQUENCE": "add-payload-size",
    },
)
def test_end_to_end_ingestion_capabilities():
    payload_to_string_plugin = ConvertPayloadValuesToString()
    payload_size_plugin = AddPayloadSizeAsColumn()
    runner = CliEntryBasedTestRunner(payload_to_string_plugin, payload_size_plugin)
    expected_object, expected_rows_object = get_shared_result_data()

    # Use a sample data job, in which `method` argument is not passed to
    # ingestion method calls.
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("no-ingest-method-job")]
    )

    cli_assert_equal(0, result)

    assert payload_size_plugin.payloads[0].payload[0] == expected_object
    assert payload_size_plugin.payloads[0].destination_table == "object_table"

    assert payload_size_plugin.payloads[1].payload[0] == expected_rows_object
    assert payload_size_plugin.payloads[1].destination_table == "tabular_table"
