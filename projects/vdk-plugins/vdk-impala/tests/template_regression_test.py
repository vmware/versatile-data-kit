# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
import re
import time
import unittest
from unittest.mock import ANY
from unittest.mock import DEFAULT
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from vdk.internal.core import errors
from vdk.plugin.impala import impala_plugin
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path


@pytest.mark.skip(
    reason="We need to test this with a recent impala instance. Current test instance is too old"
)
class TemplateRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(impala_plugin)
        time.sleep(10)  # wait for impala instance to come online

    def test_load_dimension_scd1(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_dim_org"
        target_table = "dw_dim_org"

        self._run_job(
            "load_dimension_scd1_template_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
            },
        )

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{source_view}")
        assert actual_rs.output == expected_rs.output

    def test_load_dimension_scd1_partitioned(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_dim_org_partition_test"
        target_table = "dw_dim_org_partitioned"

        self._run_job(
            "load_dimension_scd1_template_partition_job",
            {
                "source_schema": test_schema,
                "source_view": source_view,
                "target_schema": test_schema,
                "target_table": target_table,
            },
        )

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{source_view}")
        assert actual_rs.output == expected_rs.output

    def test_load_dimension_scd1_parameter_validation(self) -> None:
        self._run_template_with_bad_arguments(
            template_name="load/dimension/scd1", template_args={}, num_exp_errors=4
        )
        self._run_template_with_bad_arguments(
            template_name="load/dimension/scd1",
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
            template_name="load/dimension/scd1",
            template_args=template_args,
        )

    def test_load_dimension_scd2(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_scmdb_people"
        target_table = "dw_scmdb_people"
        expect_table = "ex_scmdb_people"

        self._run_job(
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

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        # delete first (surrogate key) column from the two results, as those are uniquely generated and might differ
        actual = {x[38:] for x in actual_rs.output.split("\n")}
        expected = {x[5:] for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            expected, actual, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_dimension_scd2_parameter_validation(self) -> None:
        self._run_template_with_bad_arguments(
            template_name="load/dimension/scd2", template_args={}, num_exp_errors=9
        )
        self._run_template_with_bad_arguments(
            template_name="load/dimension/scd2",
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
            template_name="load/dimension/scd2",
            template_args=template_args,
        )

    def test_load_versioned(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_sddc_h_updates"
        target_table = "dim_sddc_h"
        expect_table = "ex_dim_sddc_h"

        self._run_job(
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
        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")

        # delete first (surrogate key) column from the two results, as those are uniquely generated and might differ
        actual = {x[38:] for x in actual_rs.output.split("\n")}
        expected = {x[5:] for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_versioned_partitioned(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_sddc_h_updates_partition_test"
        target_table = "dim_sddc_h_partitioned"
        expect_table = "ex_dim_sddc_h_partition_test"

        self._run_job(
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

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")
        # delete first (surrogate key) column from the two results, as those are uniquely generated and might differ
        actual = {x[38:] for x in actual_rs.output.split("\n")}
        expected = {x[5:] for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_load_versioned_parameter_validation(self) -> None:
        self._run_template_with_bad_arguments(
            template_name="load/versioned", template_args={}, num_exp_errors=7
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
            template_name="load/versioned",
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
            template_name="load/versioned",
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
            template_name="load/versioned",
            template_args=template_args,
        )

    def test_load_fact_snapshot(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_sddc_daily"
        target_table = "dw_fact_sddc_daily"
        expect_table = "ex_fact_sddc_daily"

        self._run_job(
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

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")

        assert actual_rs.output == expected_rs.output

    def test_load_fact_snapshot_empty_source(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_sddc_daily_empty_source"
        target_table = "dw_fact_sddc_daily_empty_source"
        expect_table = "ex_fact_sddc_daily_empty_source"

        self._run_job(
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

        actual_rs = self._run_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self._run_query(f"SELECT * FROM {test_schema}.{expect_table}")

        assert actual_rs.output == expected_rs.output

    def test_load_fact_snapshot_partition(self) -> None:
        test_schema = "vdkprototypes"
        source_view = "vw_fact_sddc_daily_partition"
        target_table = "dw_fact_sddc_daily_partition"
        expect_table = "ex_fact_sddc_daily_partition"

        self._run_job(
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

        actual_rs = set(
            self.job_input.execute_query(f"SELECT * FROM {test_schema}.{target_table}")
        )
        expected_rs = set(
            self.job_input.execute_query(f"SELECT * FROM {test_schema}.{expect_table}")
        )

        self.assertSetEqual(
            expected_rs,
            actual_rs,
            f"Elements in {expect_table} and {target_table} differ.",
        )

    def test_load_fact_snapshot_parameter_validation(self) -> None:
        self._run_template_with_bad_arguments(
            template_name="load/fact/snapshot", template_args={}, num_exp_errors=5
        )
        self._run_template_with_bad_arguments(
            template_name="load/fact/snapshot",
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
            template_name="load/fact/snapshot",
            template_args=template_args,
        )

    def test_template_user_error(self):
        template_args = {
            "source_schema": "vdkprototypes",
            "source_view": "vw_dim_org",
            "target_schema": "vdkprototypes",
            "target_table": "dw_dim_org",
        }

        def run_job():
            self.job_input.execute_template(
                template_name="load/dimension/scd1", template_args=template_args
            )

        with patch(
            "vacloud.vdk.templates.template_executor.JobInput.execute_query",
            side_effect=[DEFAULT, Exception],
        ):  # TemplateExecutor makes 5 calls to execute_query (given 4
            # sql files in a template), errors in the first two files
            # would be due to user errors, while errors in the second two files due to
            # platform error, so we patch in an exception in the execution of the first file
            self.assertRaises(errors.DeriverCodeError, run_job)

    def test_template_platform_error(self):
        template_args = {
            "source_schema": "vdkprototypes",
            "source_view": "vw_dim_org",
            "target_schema": "vdkprototypes",
            "target_table": "dw_dim_org",
        }

        def run_job():
            self.job_input.execute_template(
                template_name="load/dimension/scd1", template_args=template_args
            )

        with patch(
            "vacloud.vdk.templates.template_executor.JobInput.execute_query",
            side_effect=[DEFAULT, DEFAULT, DEFAULT, Exception],
        ):  # TemplateExecutor makes 5 calls to execute_query (given 4
            # sql files in a template), errors in the first two files
            # would be due to user errors, while errors in the second two files due to
            # platform error, so we patch in an exception in the execution of the first file
            self.assertRaises(Exception)

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
        def just_rethrow(*_, **kwargs):
            raise kwargs["exception"]

        errors.log_and_rethrow = MagicMock(side_effect=just_rethrow)

        expected_error_regex = re.escape(
            f'{num_exp_errors} validation {"errors" if num_exp_errors > 1 else "error"} '
            f"for {template_name} template"
        )
        with self.assertRaisesRegex(Exception, expected_error_regex):
            result = self._run_job(template_name, template_args)

        errors.log_and_rethrow.assert_called_once_with(
            to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
            log=ANY,
            what_happened="Template execution in Data Job finished with error",
            why_it_happened=ANY,
            consequences=errors.MSG_CONSEQUENCE_TERMINATING_APP,
            countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION,
            exception=ANY,
        )

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
            raise Exception()

        errors.log_and_throw = MagicMock(side_effect=just_throw)

        with self.assertRaises(Exception) as context:
            self._run_job(template_name, template_args)

        errors.log_and_throw.assert_called_once_with(
            to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
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
