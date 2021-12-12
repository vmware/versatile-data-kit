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
from functional.ingestion import utils
from functional.ingestion.payload_pre_process_plugins import AddPayloadSizeAsColumn
from functional.ingestion.payload_pre_process_plugins import (
    ConvertPayloadValuesToString,
)
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin

# TODO: Add test cases for the following scenarios
# 1) INGEST_PAYLOAD_PREPROCESS_SEQUENCE=A,B in job code method = C
# 2) INGEST_PAYLOAD_PREPROCESS_SEQUENCE=A,B and VDK_INGEST_METHOD_DEFAULT=C
# 3) INGEST_PAYLOAD_PREPROCESS_SEQUENCE=A,B and VDK_INGEST_METHOD_DEFAULT=C and
#    job code is D
# 4) INGEST_PAYLOAD_PREPROCESS_SEQUENCE=""
# 5) INGEST_PAYLOAD_PREPROCESS_SEQUENCE=A,B - A,B are used for pre-processing,
#    B is used for ingesting and post-processing


log = logging.getLogger(__name__)


@mock.patch.dict(
    os.environ,
    {
        "INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "convert-to-string,add-payload-size",
        "INGEST_METHOD_DEFAULT": "memory",
    },
)
def test_chained_ingest_no_direct_method_passed():
    pre_ingest_plugin = ConvertPayloadValuesToString()
    payload_size_plugin = AddPayloadSizeAsColumn()
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(
        pre_ingest_plugin, payload_size_plugin, ingest_plugin
    )

    # TODO: Uncomment below lines when implementation is complete
    # Use a sample data job, in which `method` argument is not passed to
    # ingestion method calls.
    # result: Result = runner.invoke(["run", utils.job_path("job-with-no-method")])

    # cli_assert_equal(0, result)

    # expected_object = dict(
    #     int_key=str(42),
    #     str_key="example_str",
    #     bool_key=str(True),
    #     float_key=str(1.23),
    #     nested=str(dict(key="value")),
    # )
    # assert ingest_plugin.payloads[0].payload[0] == expected_object
    # assert ingest_plugin.payloads[0].destination_table == "object_table"

    # expected_rows_object = {"first": "two", "second": "2"}
    # assert ingest_plugin.payloads[1].payload[0] == expected_rows_object
    # assert ingest_plugin.payloads[1].destination_table == "tabular_table"


@mock.patch.dict(
    os.environ,
    {"INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "convert-to-string,add-payload-size"},
)
def test_chained_ingest_direct_method_passed():
    pre_ingest_plugin = ConvertPayloadValuesToString()
    payload_size_plugin = AddPayloadSizeAsColumn()
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(
        pre_ingest_plugin, payload_size_plugin, ingest_plugin
    )

    # Use a sample data job, in which `method` argument is passed to ingestion
    # method calls.
    result: Result = runner.invoke(["run", utils.job_path("test-ingest-job")])

    cli_assert_equal(0, result)

    # TODO: Uncomment below lines when implementation is complete
    # expected_object = dict(
    #     int_key=str(42),
    #     str_key="example_str",
    #     bool_key=str(True),
    #     float_key=str(1.23),
    #     nested=str(dict(key="value")),
    # )
    # assert ingest_plugin.payloads[0].payload[0] == expected_object
    assert ingest_plugin.payloads[0].destination_table == "object_table"

    # TODO: Uncomment below lines when implementation is complete
    # expected_rows_object = {"first": "two", "second": "2"}
    # assert ingest_plugin.payloads[1].payload[0] == expected_rows_object
    assert ingest_plugin.payloads[1].destination_table == "tabular_table"
