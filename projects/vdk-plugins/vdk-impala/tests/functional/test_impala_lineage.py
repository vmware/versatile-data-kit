# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import sys
from unittest import mock
from unittest import TestCase
from unittest.mock import patch

import pytest
from click.testing import Result
from vdk.api.lineage.model.logger.lineage_logger import ILineageLogger
from vdk.api.lineage.model.sql.model import LineageData
from vdk.api.lineage.model.sql.model import LineageTable
from vdk.api.plugin.hook_markers import hookimpl
from vdk.plugin.impala import impala_plugin
from vdk.plugin.impala.impala_lineage_plugin import LINEAGE_LOGGER_KEY
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_IMPALA_HOST = "VDK_IMPALA_HOST"
VDK_IMPALA_PORT = "VDK_IMPALA_PORT"
VDK_IMPALA_SYNC_DDL = "VDK_IMPALA_SYNC_DDL"
VDK_IMPALA_QUERY_POOL = "VDK_IMPALA_QUERY_POOL"


class TestConfigPlugin:
    def __init__(self, lineage_logger: ILineageLogger):
        self.lineage_logger = lineage_logger

    @hookimpl
    def vdk_initialize(self, context):
        # register a lineage logger which will be used to validate if correct lineage data was emitted
        context.state.set(LINEAGE_LOGGER_KEY, self.lineage_logger)


def execute_query(runner, query: str):
    result: Result = runner.invoke(["impala-query", "--query", query])
    cli_assert_equal(0, result)


@pytest.mark.skipif(
    sys.version_info >= (3, 10),
    reason="Lineage collection is not supported in python 3.10."
    "See impala_lineage_plugin.py for more details",
)
@pytest.mark.usefixtures("impala_service")
class ImpalaLineageTest(TestCase):
    @patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "IMPALA",
            VDK_IMPALA_HOST: "localhost",
            VDK_IMPALA_PORT: "21050",
        },
    )
    def test_lineage_not_collected_for_invalid_query(self):
        mock_lineage_logger = mock.MagicMock(ILineageLogger)
        runner = CliEntryBasedTestRunner(
            TestConfigPlugin(mock_lineage_logger), impala_plugin
        )
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job-syntax-error")]
        )
        cli_assert_equal(1, result)
        assert not mock_lineage_logger.send.called

    @patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "IMPALA",
            VDK_IMPALA_HOST: "localhost",
            VDK_IMPALA_PORT: "21050",
        },
    )
    def test_lineage_for_create_and_insert_queries(self):
        mock_lineage_logger = mock.MagicMock(ILineageLogger)
        runner = CliEntryBasedTestRunner(
            TestConfigPlugin(mock_lineage_logger), impala_plugin
        )
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )
        cli_assert_equal(0, result)

        class InsertLineageDataMatcher:
            def __eq__(self, lineage_data: LineageData):
                # the query is different on every run of the test as it has the opid (which is unique) prepended
                assert "INSERT INTO stocks VALUES" in lineage_data.query
                assert lineage_data.query_type is None
                assert lineage_data.query_status == "OK"
                assert lineage_data.output_table.catalog is None
                assert lineage_data.output_table.schema == "default"
                assert lineage_data.output_table.table == "stocks"
                assert len(lineage_data.input_tables) == 0  # no inputs for insert query
                return True

        # create table and select 1 queries should not result in sending lineage, hence test with called_once to verify
        # that only one lineage payload has been emitted
        mock_lineage_logger.send.assert_called_once_with(InsertLineageDataMatcher())

    @patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "IMPALA",
            VDK_IMPALA_HOST: "localhost",
            VDK_IMPALA_PORT: "21050",
        },
    )
    def test_lineage_for_scd1_template(self):
        mock_lineage_logger = mock.MagicMock(ILineageLogger)
        runner = CliEntryBasedTestRunner(
            TestConfigPlugin(mock_lineage_logger), impala_plugin
        )
        schema = "default"
        source = "scd1_source"
        target = "scd1_target"
        args = {
            "source_schema": schema,
            "source_view": source,
            "target_schema": schema,
            "target_table": target,
        }
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("load_dimension_scd1_template_job"),
                "--arguments",
                json.dumps(args),
            ]
        )
        cli_assert_equal(0, result)

        class SCD1LineageDataMatcher:
            def __init__(self, outer_instance: ImpalaLineageTest):
                self.outer_instance = outer_instance

            def __eq__(self, lineage_data: LineageData):
                assert (
                    "INSERT OVERWRITE TABLE default.scd1_target" in lineage_data.query
                )
                assert "SELECT * FROM default.scd1_source" in lineage_data.query
                assert lineage_data.query_type is None
                assert lineage_data.query_status == "OK"
                assert lineage_data.output_table.catalog is None
                assert lineage_data.output_table.schema == schema
                assert lineage_data.output_table.table == target
                expected_inputs = [LineageTable(None, schema, source)]
                self.outer_instance.assertCountEqual(
                    lineage_data.input_tables, expected_inputs
                )
                return True

        # the last emitted payload is expected to contain the lineage about the template (there are few lineage payloads
        # that describe the insert into queries used to prepare the tables for the test)
        mock_lineage_logger.send.assert_called_with(SCD1LineageDataMatcher(self))

    @patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "IMPALA",
            VDK_IMPALA_HOST: "localhost",
            VDK_IMPALA_PORT: "21050",
        },
    )
    def test_lineage_for_scd2_template(self):
        mock_lineage_logger = mock.MagicMock(ILineageLogger)
        runner = CliEntryBasedTestRunner(
            TestConfigPlugin(mock_lineage_logger), impala_plugin
        )
        schema = "default"
        source_table = "scd2_source"
        target_table = "scd2_target"
        args = {
            "source_schema": schema,
            "source_view": source_table,
            "target_schema": schema,
            "target_table": target_table,
            "staging_schema": schema,
            "expect_schema": "default",
            "expect_table": "scd2_expected",
            "start_time_column": "start_time",
            "end_time_column": "end_time",
            "end_time_default_value": "9999-12-31",
            "surrogate_key_column": "sk",
            "id_column": "id",
        }
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("load_dimension_scd2_template_job"),
                "--arguments",
                json.dumps(args),
            ]
        )
        cli_assert_equal(0, result)

        class SCD2LineageDataMatcher:
            def __init__(self, outer_instance: ImpalaLineageTest):
                self.outer_instance = outer_instance

            def __eq__(self, lineage_data: LineageData):
                assert (
                    "INSERT OVERWRITE TABLE default.scd2_target" in lineage_data.query
                )
                assert lineage_data.query_type is None
                assert lineage_data.query_status == "OK"
                assert lineage_data.output_table.catalog is None
                assert lineage_data.output_table.schema == schema
                assert lineage_data.output_table.table == target_table
                expected_inputs = [
                    LineageTable(None, schema, source_table),
                    LineageTable(None, schema, target_table),
                ]
                self.outer_instance.assertCountEqual(
                    lineage_data.input_tables, expected_inputs
                )
                return True

        # the last emitted payload is expected to contain the lineage about the template (there are few lineage payloads
        # that describe the insert into queries used to prepare the tables for the test)
        mock_lineage_logger.send.assert_called_with(SCD2LineageDataMatcher(self))

    @patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "IMPALA",
            VDK_IMPALA_HOST: "localhost",
            VDK_IMPALA_PORT: "21050",
        },
    )
    def test_lineage_for_fact_snapshot_template(self):
        mock_lineage_logger = mock.MagicMock(ILineageLogger)
        runner = CliEntryBasedTestRunner(
            TestConfigPlugin(mock_lineage_logger), impala_plugin
        )
        schema = "default"
        source_table = "fact_source"
        target_table = "fact_target"
        args = {
            "source_schema": schema,
            "source_view": source_table,
            "target_schema": schema,
            "target_table": target_table,
            "expect_schema": schema,
            "expect_table": "fact_expected",
            "last_arrival_ts": "updated_at",
        }
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("load_fact_snapshot_template_job"),
                "--arguments",
                json.dumps(args),
            ]
        )
        cli_assert_equal(0, result)

        class FactSnapshotLineageDataMatcher:
            def __init__(self, outer_instance: ImpalaLineageTest):
                self.outer_instance = outer_instance

            def __eq__(self, lineage_data: LineageData):
                assert (
                    "INSERT OVERWRITE TABLE default.fact_target" in lineage_data.query
                )
                assert lineage_data.query_type is None
                assert lineage_data.query_status == "OK"
                assert lineage_data.output_table.catalog is None
                assert lineage_data.output_table.schema == schema
                assert lineage_data.output_table.table == target_table
                expected_inputs = [
                    LineageTable(None, schema, source_table),
                    LineageTable(None, schema, target_table),
                ]
                self.outer_instance.assertCountEqual(
                    lineage_data.input_tables, expected_inputs
                )
                return True

        # the last emitted payload is expected to contain the lineage about the template (there are few lineage payloads
        # that describe the insert into queries used to prepare the tables for the test)
        mock_lineage_logger.send.assert_called_with(
            FactSnapshotLineageDataMatcher(self)
        )

    @patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "IMPALA",
            VDK_IMPALA_HOST: "localhost",
            VDK_IMPALA_PORT: "21050",
        },
    )
    def test_lineage_for_load_versioned_template(self):
        mock_lineage_logger = mock.MagicMock(ILineageLogger)
        runner = CliEntryBasedTestRunner(
            TestConfigPlugin(mock_lineage_logger), impala_plugin
        )
        schema = "default"
        source_table = "versioned_source"
        target_table = "versioned_target"
        args = {
            "source_schema": schema,
            "source_view": source_table,
            "target_schema": schema,
            "target_table": target_table,
            "expect_schema": schema,
            "expect_table": "versioned_expect",
            "id_column": "sddc_id",
            "sk_column": "sddc_sk",
            "value_columns": [
                "updated_by_user_id",
                "state",
                "is_nsxt",
                "cloud_vendor",
                "version",
            ],
            "tracked_columns": [
                "updated_by_user_id",
                "state",
                "is_nsxt",
                "version",
            ],
            "active_from_column": "active_from",
            "active_to_column": "active_to",
            "active_to_max_value": "9999-12-31",
            "updated_at_column": "updated_at",
        }
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("load_versioned_template_job"),
                "--arguments",
                json.dumps(args),
            ]
        )
        cli_assert_equal(0, result)

        class VersionedTemplateLineageDataMatcher:
            def __init__(self, outer_instance: ImpalaLineageTest):
                self.outer_instance = outer_instance

            def __eq__(self, lineage_data: LineageData):
                assert (
                    "INSERT OVERWRITE TABLE default.versioned_target"
                    in lineage_data.query
                )
                assert lineage_data.query_type is None
                assert lineage_data.query_status == "OK"
                assert lineage_data.output_table.catalog is None
                assert lineage_data.output_table.schema == schema
                assert lineage_data.output_table.table == target_table
                expected_inputs = [
                    LineageTable(None, schema, source_table),
                    LineageTable(None, schema, target_table),
                ]
                self.outer_instance.assertCountEqual(
                    lineage_data.input_tables, expected_inputs
                )
                return True

        # the last emitted payload is expected to contain the lineage about the template (there are few lineage payloads
        # that describe the insert into queries used to prepare the tables for the test)
        mock_lineage_logger.send.assert_called_with(
            VersionedTemplateLineageDataMatcher(self)
        )

    @patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "IMPALA",
            VDK_IMPALA_HOST: "localhost",
            VDK_IMPALA_PORT: "21050",
        },
    )
    def test_lineage_for_non_lineage_queries(self):
        mock_lineage_logger = mock.MagicMock(ILineageLogger)
        runner = CliEntryBasedTestRunner(
            TestConfigPlugin(mock_lineage_logger), impala_plugin
        )
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job-non-lineage")]
        )
        cli_assert_equal(0, result)

        # create table and computing its stats should not result in creating lineage event
        mock_lineage_logger.send.assert_not_called()
