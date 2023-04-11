# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import unittest
from unittest.mock import patch

from click.testing import Result
from vdk.plugin.gdp.execution_id import gdp_execution_id_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


class GdpExecutionIdTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__ingest_plugin = IngestIntoMemoryPlugin()
        self.__runner = CliEntryBasedTestRunner(
            self.__ingest_plugin, gdp_execution_id_plugin
        )

    @patch.dict(
        os.environ,
        {
            "VDK_INGEST_METHOD_DEFAULT": "memory",
            "VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "gdp-execution-id",
        },
    )
    def test_ingested_payload_expansion(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )
        cli_assert_equal(0, result)

        assert len(self.__ingest_plugin.payloads) > 0
        payloads = self.__ingest_plugin.payloads[0].payload
        assert len(payloads) == 3
        for p in payloads:
            assert "vdk_gdp_execution_id" in p.keys()
            assert p["vdk_gdp_execution_id"] is not None
            assert f"\"execution_id\": \"{p['vdk_gdp_execution_id']}\"" in result.output

    @patch.dict(
        os.environ,
        {
            "VDK_INGEST_METHOD_DEFAULT": "memory",
            "VDK_INGEST_PAYLOAD_PREPROCESS_SEQUENCE": "gdp-execution-id",
            "VDK_GDP_EXECUTION_ID_MICRO_DIMENSION_NAME": "micro_dimension_name_customized",
        },
    )
    def test_micro_dimension_name_configurable(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )
        cli_assert_equal(0, result)

        assert len(self.__ingest_plugin.payloads) > 0
        payloads = self.__ingest_plugin.payloads[0].payload
        assert len(payloads) == 3
        for p in payloads:
            assert "micro_dimension_name_customized" in p.keys()
            assert p["micro_dimension_name_customized"] is not None
            assert (
                f"\"execution_id\": \"{p['micro_dimension_name_customized']}\""
                in result.output
            )
