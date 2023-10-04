# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
import re
import time
import unittest
from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from vdk.internal.core import errors
from vdk.internal.core.errors import ResolvableBy
from vdk.plugin.impala import impala_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_IMPALA_HOST = "VDK_IMPALA_HOST"
VDK_IMPALA_PORT = "VDK_IMPALA_PORT"


@patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "IMPALA",
        VDK_IMPALA_HOST: "localhost",
        VDK_IMPALA_PORT: "21050",
    },
)
@pytest.mark.usefixtures("impala_service")
class TestTemplateRegression(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(impala_plugin)
        time.sleep(10)  # wait for impala instance to come online
        self._run_query("CREATE DATABASE IF NOT EXISTS vdkprototypes")
        self._run_query("CREATE DATABASE IF NOT EXISTS staging_vdkprototypes")

    def test_load_dimension_scd1(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_dim_org"
        target_table = "dw_dim_org"

        res = self._run_job(
            "load_dimension_scd1_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
            },
        )
        cli_assert(not res.exception, res)
        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{source_view}")
        assert actual_rs.output and expected_rs.output
        assert actual_rs.output == expected_rs.output

    def test_load_dimension_scd1_partitioned(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_dim_org_partition_test"
        target_table = "dw_dim_org_partitioned"

        res = self._run_job(
            "load_dimension_scd1_template_partition_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
            },
        )
        cli_assert(not res.exception, res)

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{source_view}")

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        assert actual_rs.output and expected_rs.output
        self.assertSetEqual(
            expected, actual, f"Elements in {source_view} and {target_table} differ."
        )

    def test_load_dimension_scd1_parameter_validation(self) -> None:
        self._run_template_with_bad_arguments(
            template_name="load_dimension_scd1_template_only",
            template_args={},
            num_exp_errors=4,
        )
        self._run_template_with_bad_arguments(
            template_name="load_dimension_scd1_template_only",
            template_args={"source_view": "foo", "extra_parameter": "bar"},
            num_exp_errors=3,
        )

    def test_load_dimension_scd1_bad_target_schema(self) -> None:
        template_args = {
            "source_schema": "vdkprototypes",
            "source_view": "vw_dim_org",
            "target_schema": "vdkprototypes",
            "target_table": "dw_dim_org_as_textfile",
        }

        self._run_template_with_bad_target_schema(
            template_name="load_dimension_scd1_template_only",
            template_args=template_args,
        )

    def test_load_dimension_scd1_checks_positive(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_dim_org_check_positive"
        target_table = "dw_dim_org_check_positive"
        staging_schema = "staging_vdkprototypes"

        res = self._run_job(
            "load_dimension_scd1_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "check": "use_positive_check",
                "staging_schema": staging_schema,
            },
        )

        cli_assert(not res.exception, res)
        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{source_view}")
        assert actual_rs.output and expected_rs.output
        assert actual_rs.output == expected_rs.output

    def test_load_dimension_scd1_checks_negative(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_dim_org_check_negative"
        target_table = "dw_dim_org_check_negative"
        staging_schema = "staging_vdkprototypes"

        res = self._run_job(
            "load_dimension_scd1_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "check": "use_negative_check",
                "staging_schema": staging_schema,
            },
        )

        assert res.exception
        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{source_view}")
        assert actual_rs.output and expected_rs.output
        assert actual_rs.output != expected_rs.output

    def test_load_dimension_scd2(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_scmdb_people"
        target_table = "dw_scmdb_people"
        expect_table = "ex_scmdb_people"

        res = self._run_job(
            "load_dimension_scd2_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "staging_schema": test_schema,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "start_time_column": "start_time",
                "end_time_column": "end_time",
                "end_time_default_value": "9999-12-31",
                "surrogate_key_column": "sk",
                "id_column": "id",
            },
        )
        cli_assert(not res.exception, res)

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        # delete first (surrogate key) column from the two results, as those are uniquely generated and might differ
        actual = {x[38:] for x in actual_rs.output.split("\n")}
        expected = {x[5:] for x in expected_rs.output.split("\n")}
        assert actual_rs.output and expected_rs.output
        self.assertSetEqual(
            expected, actual, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_dimension_scd2_parameter_validation(self) -> None:
        self._run_template_with_bad_arguments(
            template_name="load_dimension_scd2_template_only",
            template_args={},
            num_exp_errors=9,
        )
        self._run_template_with_bad_arguments(
            template_name="load_dimension_scd2_template_only",
            template_args={"source_view": "foo", "extra_parameter": "bar"},
            num_exp_errors=8,
        )

    def test_load_dimension_scd2_bad_target_schema(self) -> None:
        template_args = {
            "source_schema": "vdkprototypes",
            "source_view": "vw_scmdb_people",
            "target_schema": "vdkprototypes",
            "target_table": "dw_fact_sddc_daily_as_textfile",
            "staging_schema": "vdkprototypes",
            "start_time_column": "start_time",
            "end_time_column": "end_time",
            "end_time_default_value": "9999-12-31",
            "surrogate_key_column": "sk",
            "id_column": "id",
        }

        self._run_template_with_bad_target_schema(
            template_name="load_dimension_scd2_template_only",
            template_args=template_args,
        )

    def test_load_versioned(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_sddc_h_updates"
        target_table = "dim_sddc_h"
        expect_table = "ex_dim_sddc_h"

        res = self._run_job(
            "load_versioned_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
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
            },
        )
        cli_assert(not res.exception, res)

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output
        # delete first (surrogate key) column from the two results, as those are uniquely generated and might differ
        actual = {x[38:] for x in actual_rs.output.split("\n")}
        expected = {x[12:] for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_versioned_partitioned(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_sddc_h_updates_partition_test"
        target_table = "dim_sddc_h_partitioned"
        expect_table = "ex_dim_sddc_h_partition_test"

        res = self._run_job(
            "load_versioned_template_partition_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
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
            },
        )
        cli_assert(not res.exception, res)

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output
        # delete first (surrogate key) column from the two results, as those are uniquely generated and might differ
        actual = {x[38:] for x in actual_rs.output.split("\n")}
        expected = {x[12:] for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_versioned_parameter_validation(self) -> None:
        self._run_template_with_bad_arguments(
            template_name="load_versioned_template_only",
            template_args={},
            num_exp_errors=7,
        )

        good_template_args = {
            "source_schema": "vdkprototypes",
            "source_view": "vw_sddc_h_updates",
            "target_schema": "vdkprototypes",
            "target_table": "dim_sddc_h_as_textfile",
            "id_column": "sddc_id",
            "sk_column": "sddc_sk",
            "value_columns": [
                "updated_by_user_id",
                "state",
                "is_nsxt",
                "cloud_vendor",
                "version",
            ],
            "tracked_columns": ["updated_by_user_id", "state", "is_nsxt", "version"],
            "active_from_column": "active_from",
            "active_to_column": "active_to",
            "active_to_max_value": "9999-12-31",
            "updated_at_column": "updated_at",
            "extra_parameter": "bar",
        }

        self._run_template_with_bad_arguments(
            template_name="load_versioned_template_only",
            template_args={
                **good_template_args,
                **{
                    "value_columns": [
                        "updated_by_user_id",
                        "state",
                        "is_nsxt",
                        "cloud_vendor",
                    ],
                    "tracked_columns": [
                        "updated_by_user_id",
                        "state",
                        "is_nsxt",
                        "version",
                    ],
                },
            },
            num_exp_errors=1,
        )

        self._run_template_with_bad_arguments(
            template_name="load_versioned_template_only",
            template_args={
                **good_template_args,
                **{
                    "value_columns": [
                        "updated_by_user_id",
                        "state",
                        "is_nsxt",
                        "cloud_vendor",
                    ],
                    "tracked_columns": [],
                },
            },
            num_exp_errors=1,
        )

    def test_load_versioned_bad_target_schema(self) -> None:
        template_args = {
            "source_schema": "vdkprototypes",
            "source_view": "vw_sddc_h_updates",
            "target_schema": "vdkprototypes",
            "target_table": "dim_sddc_h_as_textfile",
            "id_column": "sddc_id",
            "sk_column": "sddc_sk",
            "value_columns": [
                "updated_by_user_id",
                "state",
                "is_nsxt",
                "cloud_vendor",
                "version",
            ],
            "tracked_columns": ["updated_by_user_id", "state", "is_nsxt", "version"],
            "active_from_column": "active_from",
            "active_to_column": "active_to",
            "active_to_max_value": "9999-12-31",
            "updated_at_column": "updated_at",
        }

        self._run_template_with_bad_target_schema(
            template_name="load_versioned_template_only",
            template_args=template_args,
        )

    def test_load_fact_snapshot(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_sddc_daily"
        target_table = "dw_fact_sddc_daily"
        expect_table = "ex_fact_sddc_daily"

        res = self._run_job(
            "load_fact_snapshot_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "last_arrival_ts": "updated_at",
            },
        )
        cli_assert(not res.exception, res)

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_fact_snapshot_empty_source(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_sddc_daily_empty_source"
        target_table = "dw_fact_sddc_daily_empty_source"
        expect_table = "ex_fact_sddc_daily_empty_source"

        res = self._run_job(
            "load_fact_snapshot_template_job_empty_source",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "last_arrival_ts": "updated_at",
            },
        )
        # Expecting data job not to finish due to empty source.
        cli_assert(not res.exception, res)
        assert res.exit_code == 0

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_fact_snapshot_partition(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_sddc_daily_partition"
        target_table = "dw_fact_sddc_daily_partition"
        expect_table = "ex_fact_sddc_daily_partition"

        res = self._run_job(
            "load_fact_snapshot_template_partition_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "last_arrival_ts": "updated_at",
            },
        )
        cli_assert(not res.exception, res)

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_fact_snapshot_parameter_validation(self) -> None:
        self._run_template_with_bad_arguments(
            template_name="load_fact_snapshot_template_only",
            template_args={},
            num_exp_errors=5,
        )
        self._run_template_with_bad_arguments(
            template_name="load_fact_snapshot_template_only",
            template_args={"source_view": "foo", "target_table": None},
            num_exp_errors=4,
        )

    def test_load_fact_snapshot_bad_target_schema(self) -> None:
        template_args = {
            "source_schema": "vdkprototypes",
            "source_view": "vw_fact_sddc_daily",
            "target_schema": "vdkprototypes",
            "target_table": "dw_fact_sddc_daily_as_textfile",
            "expect_schema": "vdkprototypes",
            "last_arrival_ts": "updated_at",
        }

        self._run_template_with_bad_target_schema(
            template_name="load_fact_snapshot_template_only",
            template_args=template_args,
        )

    def test_load_fact_snapshot_checks_positive(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_sddc_daily_check_positive"
        target_table = "fact_sddc_daily_check_positive"
        staging_schema = "staging_vdkprototypes"
        expect_table = "ex_fact_sddc_daily_check_positive"

        res = self._run_job(
            "load_fact_snapshot_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "last_arrival_ts": "updated_at",
                "check": "use_positive_check",
                "staging_schema": staging_schema,
            },
        )

        cli_assert(not res.exception, res)
        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_fact_snapshot_checks_negative(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_sddc_daily_check_negative"
        target_table = "fact_sddc_daily_check_negative"
        staging_schema = "staging_vdkprototypes"
        expect_table = "ex_fact_sddc_daily_check_negative"

        res = self._run_job(
            "load_fact_snapshot_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "last_arrival_ts": "updated_at",
                "check": "use_negative_check",
                "staging_schema": staging_schema,
            },
        )

        assert res.exception
        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output
        assert actual_rs.output != expected_rs.output

    def _run_job(self, job_name: str, args: dict):
        return self.__runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    job_name,
                ),
                "--arguments",
                json.dumps(args),
            ]
        )

    def _run_query(self, query_string):
        return self.__runner.invoke(
            [
                "impala-query",
                "--query",
                query_string,
            ]
        )

    def _run_template_with_bad_arguments(
        self, template_name: str, template_args: dict, num_exp_errors: int
    ) -> None:
        expected_error_regex = re.escape(
            f'{num_exp_errors} validation {"errors" if num_exp_errors > 1 else "error"} '
            f"for {template_name} template"
        )

        def just_rethrow(*_, **kwargs):
            raise Exception(expected_error_regex)

        with patch.object(errors, "log_and_rethrow") as patched_log_and_rethrow:
            patched_log_and_rethrow.side_effect = just_rethrow
            result = self._run_job(template_name, template_args)
            assert expected_error_regex in result.output, result.output
            assert errors.log_and_rethrow.call_args[1]["what_happened"], result.output
            assert (
                f"{num_exp_errors} validation error"
                in errors.log_and_rethrow.call_args[1]["why_it_happened"]
                or f"{num_exp_errors}\\ validation\\ error"
                in errors.log_and_rethrow.call_args[1]["why_it_happened"]
            ), result.output
            assert errors.log_and_rethrow.call_args[1]["consequences"], result.output
            assert errors.log_and_rethrow.call_args[1]["countermeasures"], result.output

    def _run_template_with_bad_target_schema(
        self, template_name: str, template_args: dict
    ) -> None:
        self._run_query(
            """
            DROP TABLE IF EXISTS {target_schema}.{target_table}
        """.format(
                **template_args
            )
        )
        self._run_query(
            """
            CREATE TABLE {target_schema}.{target_table} (
                attr_a INT,
                attr_b STRING,
                updated_at TIMESTAMP
            ) STORED AS TEXTFILE
        """.format(
                **template_args
            )
        )
        self._run_query(
            """
            REFRESH {target_schema}.{target_table}
        """.format(
                **template_args
            )
        )

        table_name = "`{target_schema}`.`{target_table}`".format(**template_args)

        expected_why_it_happened_msg = (
            f'The target table {table_name} must be created with a "STORED AS PARQUET" '
            f"clause. Please change the table definition accordingly and re-create the table."
        )

        def just_throw(*_, **kwargs):
            raise Exception(expected_why_it_happened_msg)

        with patch(
            "vdk.internal.core.errors.log_and_throw", MagicMock(side_effect=just_throw)
        ):
            res = self._run_job(template_name, template_args)
            assert expected_why_it_happened_msg in res.output
            errors.log_and_throw.assert_called_once_with(
                to_be_fixed_by=ResolvableBy.USER_ERROR,
                log=ANY,
                what_happened="Data loading has failed.",
                why_it_happened=(
                    f"You are trying to load data into a table {table_name} with an unsupported format. "
                    f"Currently only Parquet table format is supported."
                ),
                consequences="Data load will be aborted.",
                countermeasures=(
                    "Make sure that the destination table is stored as parquet: "
                    "https://www.cloudera.com/documentation/enterprise/5-11-x/topics/impala_parquet.html"
                    "#parquet_ddl"
                ),
            )

    def test_insert(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_vmc_utilization_cpu_mem_every5min_daily"
        target_table = "dw_fact_vmc_utilization_cpu_mem_every5min_daily"
        expect_table = "ex_fact_vmc_utilization_cpu_mem_every5min_daily"

        res = self._run_job(
            "insert_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
            },
        )
        cli_assert(not res.exception, res)

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_insert_partition(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_vmc_utilization_cpu_mem_every5min_daily_partition"
        target_table = "dw_fact_vmc_utilization_cpu_mem_every5min_daily_partition"
        expect_table = "ex_fact_vmc_utilization_cpu_mem_every5min_daily_partition"

        res = self._run_job(
            "insert_template_partition_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
            },
        )
        cli_assert(not res.exception, res)

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_insert_checks_positive(self) -> None:
        test_schema = "vdkprototypes"
        staging_schema = "staging_vdkprototypes"
        source_view = "vw_fact_vmc_utilization_cpu_mem_every5min_daily_check_positive"
        target_table = "dw_fact_vmc_utilization_cpu_mem_every5min_daily_check_positive"
        expect_table = "ex_fact_vmc_utilization_cpu_mem_every5min_daily_check_positive"

        res = self._run_job(
            "insert_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "check": "use_positive_check",
                "staging_schema": staging_schema,
            },
        )

        cli_assert(not res.exception, res)
        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_insert_checks_negative(self) -> None:
        test_schema = "vdkprototypes"
        staging_schema = "staging_vdkprototypes"
        source_view = "vw_fact_vmc_utilization_cpu_mem_every5min_daily_check_negative"
        target_table = "dw_fact_vmc_utilization_cpu_mem_every5min_daily_check_negative"
        expect_table = "ex_fact_vmc_utilization_cpu_mem_every5min_daily_check_negative"

        res = self._run_job(
            "insert_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "check": "use_negative_check",
                "staging_schema": staging_schema,
            },
        )

        assert res.exception
        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output
        assert actual_rs.output != expected_rs.output

    def test_insert_clean_staging(self) -> None:
        test_schema = "vdkprototypes"
        staging_schema = "staging_vdkprototypes"
        source_view = "vw_fact_vmc_utilization_cpu_mem_every5min_daily_clean_staging"
        target_table = "dw_fact_vmc_utilization_cpu_mem_every5min_daily_clean_staging"
        expect_table = "ex_fact_vmc_utilization_cpu_mem_every5min_daily_clean_staging"

        res_first_exec = self._run_job(
            "insert_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "check": "use_positive_check",
                "staging_schema": staging_schema,
            },
        )
        staging_table_name = f"vdk_check_{test_schema}_{target_table}"
        first_exec_rs = self._run_query(
            f"SELECT * FROM {staging_schema}.{staging_table_name}"
        )
        cli_assert_equal(0, res_first_exec)

        res_second_exec = self._run_job(
            "insert_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
                "expect_schema": test_schema,
                "expect_table": expect_table,
                "check": "use_positive_check",
                "staging_schema": staging_schema,
            },
        )
        cli_assert_equal(0, res_second_exec)

        second_exec_rs = self._run_query(
            f"SELECT * FROM {staging_schema}.{staging_table_name}"
        )
        first_exec = {x for x in first_exec_rs.output.split("\n")}
        second_exec = {x for x in second_exec_rs.output.split("\n")}

        self.assertSetEqual(
            first_exec,
            second_exec,
            f"Clean up of staging table - {staging_table_name} is not made properly. Different data was found in the table after consecutive executions.",
        )
