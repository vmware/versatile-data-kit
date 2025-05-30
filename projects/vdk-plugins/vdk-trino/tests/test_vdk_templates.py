# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
import unittest
import uuid
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.test_utils.util_funcs import cli_assert
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path
from vdk.plugin.trino import trino_plugin
from vdk.plugin.trino.trino_utils import TrinoTemplateQueries

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"
VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY = (
    "VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY"
)
VDK_LOG_EXECUTION_RESULT = "VDK_LOG_EXECUTION_RESULT"

org_move_data_to_table = TrinoTemplateQueries.move_data_to_table


def trino_move_data_to_table_break_tmp_to_target(
    obj, from_db: str, from_table_name: str, to_db: str, to_table_name: str
):
    if from_table_name.startswith("tmp_dw_people") and to_table_name.startswith(
        "dw_people"
    ):
        obj.drop_table(from_db, from_table_name)
    return org_move_data_to_table(obj, from_db, from_table_name, to_db, to_table_name)


def trino_move_data_to_table_break_tmp_to_target_and_restore(
    obj, from_db: str, from_table_name: str, to_db: str, to_table_name: str
):
    if from_table_name.startswith("tmp_dw_people") and to_table_name.startswith(
        "dw_people"
    ):
        obj.drop_table(from_db, from_table_name)

    if from_table_name.startswith("backup_dw_people") and to_table_name.startswith(
        "dw_people"
    ):
        obj.drop_table(from_db, from_table_name)

    return org_move_data_to_table(obj, from_db, from_table_name, to_db, to_table_name)


@pytest.fixture(autouse=True)
def mock_os_environ():
    with mock.patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "TRINO",
            VDK_TRINO_PORT: "8080",
            VDK_TRINO_USE_SSL: "False",
            VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY: "INSERT_SELECT",
            VDK_LOG_EXECUTION_RESULT: "True",
        },
    ):
        yield


@pytest.mark.usefixtures("trino_service")
class TestTemplates(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(trino_plugin)
        self.__schema = f"source_{uuid.uuid4().hex[:10]}"
        self.__trino_query("create schema " + self.__schema)

    def test_scd1_template(self) -> None:
        source_schema = self.__schema
        source_view = "vw_dim_org"
        target_schema = self.__schema
        target_table = "dw_dim_org"

        result: Result = self.__runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "load_dimension_scd1_template_job",
                ),
                "--arguments",
                json.dumps(
                    {
                        "source_schema": source_schema,
                        "source_view": source_view,
                        "target_schema": target_schema,
                        "target_table": target_table,
                    }
                ),
            ]
        )

        cli_assert_equal(0, result)

        # refactor below to use vdk-trino-query
        actual_rs: Result = self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"""
                SELECT * FROM "{target_schema}"."{target_table}"
                """,
            ]
        )

        expected_rs: Result = self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"""
                SELECT * FROM "{source_schema}"."{source_view}"
                """,
            ]
        )

        cli_assert_equal(0, actual_rs)
        cli_assert_equal(0, expected_rs)
        assert (
            actual_rs.output == expected_rs.output
        ), f"Elements in {source_view} and {target_table} differ."

    def test_scd1_template_using_rename_strategy(self) -> None:
        with mock.patch.dict(
            os.environ,
            {VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY: "RENAME"},
        ):
            self.test_scd1_template()

    def test_scd1_template_reserved_args(self) -> None:
        source_schema = self.__schema
        source_view = "alter"
        target_schema = self.__schema
        target_table = "table"

        result: Result = self.__runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "load_dimension_scd1_template_job",
                ),
                "--arguments",
                json.dumps(
                    {
                        "source_schema": source_schema,
                        "source_view": source_view,
                        "target_schema": target_schema,
                        "target_table": target_table,
                    }
                ),
            ]
        )

        cli_assert_equal(0, result)

        actual_rs: Result = self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"""
                SELECT * FROM "{target_schema}"."{target_table}"
                """,
            ]
        )

        expected_rs: Result = self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"""
                SELECT * FROM "{source_schema}"."{source_view}"
                """,
            ]
        )

        cli_assert_equal(0, actual_rs)
        cli_assert_equal(0, expected_rs)
        assert (
            actual_rs.output == expected_rs.output
        ), f"Elements in {source_view} and {target_table} differ."

    def test_scd2_template(self) -> None:
        test_schema = self.__schema
        source_view = "vw_people_scd2"
        target_table = "dw_people_scd2"
        expect_table = "ex_people_scd2"

        result: Result = self.__scd2_template_execute(
            test_schema, source_view, target_table, expect_table
        )
        cli_assert_equal(0, result)

        # Check if we got the expected result and successfully dropped backup
        self.__scd2_template_check_expected_res(test_schema, target_table, expect_table)
        cli_assert_equal(
            1, self.__template_table_exists(test_schema, "backup_" + target_table)
        )

    def test_scd2_template_using_rename_strategy(self) -> None:
        with mock.patch.dict(
            os.environ,
            {VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY: "RENAME"},
        ):
            self.test_scd2_template()

    def test_scd2_template_reserved_args(self) -> None:
        test_schema = self.__schema
        source_view = "alter"
        target_table = "table"
        expect_table = "between"

        result: Result = self.__scd2_template_execute(
            test_schema, source_view, target_table, expect_table, False, "reserved"
        )
        cli_assert_equal(0, result)

        # Check if we got the expected result and successfully dropped backup
        self.__scd2_template_check_expected_res(
            test_schema, target_table, expect_table, "reserved"
        )
        cli_assert_equal(
            1, self.__template_table_exists(test_schema, "backup_" + target_table)
        )

    def test_scd2_template_restore_target_from_backup_on_start(self) -> None:
        test_schema = self.__schema
        source_view = "vw_people_scd2_restore"
        target_table = "dw_people_scd2_restore"
        expect_table = "ex_people_scd2_restore"

        result: Result = self.__scd2_template_execute(
            test_schema, source_view, target_table, expect_table, True
        )
        cli_assert_equal(0, result)

        assert (
            f"Successfully recovered {test_schema}.{target_table}" in result.output
        ), "Missing log for recovering target schema."

        self.__scd2_template_check_expected_res(test_schema, target_table, expect_table)

    def test_fact_periodic_snapshot_template(self) -> None:
        test_schema = self.__schema
        source_view = "vw_fact_sddc_daily"
        target_table = "dw_fact_sddc_daily"
        expect_table = "ex_fact_sddc_daily"

        result: Result = self.__fact_periodic_snapshot_template_execute(
            test_schema, source_view, target_table, expect_table
        )
        cli_assert_equal(0, result)

        self.__fact_periodic_snapshot_template_check_expected_res(
            test_schema, target_table, expect_table
        )

    def test_fact_periodic_snapshot_template_using_rename_strategy(self) -> None:
        with mock.patch.dict(
            os.environ,
            {VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY: "RENAME"},
        ):
            self.test_fact_periodic_snapshot_template()

    def test_fact_periodic_snapshot_template_reserved_args(self) -> None:
        test_schema = self.__schema
        source_view = "alter"
        target_table = "table"
        expect_table = "between"

        result: Result = self.__fact_periodic_snapshot_template_execute(
            test_schema, source_view, target_table, expect_table
        )
        cli_assert_equal(0, result)

        self.__fact_periodic_snapshot_template_check_expected_res(
            test_schema, target_table, expect_table
        )

    def test_fact_periodic_snapshot_empty_source(self) -> None:
        test_schema = self.__schema
        source_view = "vw_fact_sddc_daily_empty_source"
        target_table = "dw_fact_sddc_daily_empty_source"
        expect_table = "ex_fact_sddc_daily_empty_source"

        result: Result = self.__runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "load_fact_periodic_snapshot_template_job_empty_source",
                ),
                "--arguments",
                json.dumps(
                    {
                        "source_schema": test_schema,
                        "source_view": source_view,
                        "target_schema": test_schema,
                        "target_table": target_table,
                        "expect_schema": test_schema,
                        "expect_table": expect_table,
                        "last_arrival_ts": "updated_at",
                    }
                ),
            ]
        )
        cli_assert_equal(0, result)

        assert (
            f"Target table {test_schema}.{target_table} remains unchanged"
            in result.output
        ), "Cannot find log about empty source in output."

        self.__fact_periodic_snapshot_template_check_expected_res(
            test_schema, target_table, expect_table
        )

    def test_fact_periodic_snapshot_template_restore_target_from_backup_on_start(
        self,
    ) -> None:
        test_schema = self.__schema
        source_view = "vw_people_fact_restore"
        target_table = "dw_people_fact_restore"
        expect_table = "ex_people_fact_restore"

        result: Result = self.__fact_periodic_snapshot_template_execute(
            test_schema, source_view, target_table, expect_table, True
        )
        cli_assert_equal(0, result)

        assert (
            f"Successfully recovered {test_schema}.{target_table}" in result.output
        ), "Missing log for recovering target schema."

        self.__fact_periodic_snapshot_template_check_expected_res(
            test_schema, target_table, expect_table
        )

    def __fact_periodic_snapshot_template_execute(
        self,
        test_schema,
        source_view,
        target_table,
        expect_table,
        restore_from_backup=False,
    ):
        return self.__runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "load_fact_periodic_snapshot_template_job",
                ),
                "--arguments",
                json.dumps(
                    {
                        "source_schema": test_schema,
                        "source_view": source_view,
                        "target_schema": test_schema,
                        "target_table": target_table,
                        "expect_schema": test_schema,
                        "expect_table": expect_table,
                        "last_arrival_ts": "updated_at",
                        "test_restore_from_backup": f"{restore_from_backup}",
                    }
                ),
            ]
        )

    def __fact_periodic_snapshot_template_check_expected_res(
        self, test_schema, target_table, expect_table
    ) -> None:
        actual_rs: Result = self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"""
                SELECT * FROM "{test_schema}"."{target_table}" ORDER BY dim_date_id, dim_sddc_sk
                """,
            ]
        )

        expected_rs: Result = self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"""
                SELECT * FROM "{test_schema}"."{expect_table}" ORDER BY dim_date_id, dim_sddc_sk
                """,
            ]
        )

        cli_assert_equal(0, actual_rs)
        cli_assert_equal(0, expected_rs)
        assert actual_rs.output == expected_rs.output, (
            f"Elements in {target_table} and {expect_table} differ. "
            f"found difference: {actual_rs.output} and {expected_rs.output}"
        )

    def __scd2_template_execute(
        self,
        test_schema,
        source_view,
        target_table,
        expect_table,
        restore_from_backup=False,
        reserved=False,
    ):
        value_column_1 = reserved and "with" or "updated_by_user_id"
        return self.__runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "load_versioned_scd2_template_job",
                ),
                "--arguments",
                json.dumps(
                    {
                        "source_schema": test_schema,
                        "source_view": source_view,
                        "target_schema": test_schema,
                        "target_table": target_table,
                        "staging_schema": test_schema,
                        "expect_schema": test_schema,
                        "expect_table": expect_table,
                        "id_column": reserved and "when" or "sddc_id",
                        "sk_column": reserved and "where" or "sddc_sk",
                        "value_columns": [
                            value_column_1,
                            "state",
                            "is_next",
                            "cloud_vendor",
                            "version",
                        ],
                        "tracked_columns": [
                            value_column_1,
                            "state",
                            "is_next",
                            "version",
                        ],
                        "active_from_column": "active_from",
                        "active_to_column": "active_to",
                        "active_to_max_value": "9999-12-31",
                        "updated_at_column": "updated_at",
                        "test_restore_from_backup": f"{restore_from_backup}",
                        "value_column_1": f"{value_column_1}",
                    }
                ),
            ]
        )

    def __scd2_template_check_expected_res(
        self, test_schema, target_table, expect_table, reserved=False
    ) -> None:
        # don't check first (surrogate key) column from the two results,
        # as those are uniquely generated and might differ

        if reserved:
            actual_rs: Result = self.__runner.invoke(
                [
                    "trino-query",
                    "--query",
                    f"""
                    SELECT active_from, active_to, "when", "with", state, is_next, cloud_vendor, version
                    FROM "{test_schema}"."{target_table}"
                    ORDER BY "when", active_to
                    """,
                ]
            )

            expected_rs: Result = self.__runner.invoke(
                [
                    "trino-query",
                    "--query",
                    f"""SELECT active_from, active_to, "when", "with", state, is_next, cloud_vendor, version
                    FROM "{test_schema}"."{expect_table}"
                    ORDER BY "when", active_to""",
                ]
            )
        else:
            actual_rs: Result = self.__runner.invoke(
                [
                    "trino-query",
                    "--query",
                    f"""SELECT active_from, active_to, sddc_id, updated_by_user_id, state, is_next, cloud_vendor, version
                                FROM "{test_schema}"."{target_table}"
                                ORDER BY sddc_id, active_to""",
                ]
            )

            expected_rs: Result = self.__runner.invoke(
                [
                    "trino-query",
                    "--query",
                    f"""SELECT active_from, active_to, sddc_id, updated_by_user_id, state, is_next, cloud_vendor, version
                                FROM "{test_schema}"."{expect_table}"
                                ORDER BY sddc_id, active_to""",
                ]
            )

        cli_assert_equal(0, actual_rs)
        cli_assert_equal(0, expected_rs)
        assert (
            actual_rs.output == expected_rs.output
        ), f"Elements in {target_table} and {expect_table} differ."

    def test_insert(self) -> None:
        test_schema = self.__schema
        source_view = "vw_fact_vmc_utilization_cpu_mem_every5min_daily"
        target_table = "dw_fact_vmc_utilization_cpu_mem_every5min_daily"
        expect_table = "ex_fact_vmc_utilization_cpu_mem_every5min_daily"

        res = self.__fact_insert_template_execute(
            test_schema, source_view, target_table, expect_table
        )

        cli_assert(not res.exception, res)

        actual_rs = self.__trino_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self.__trino_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_insert_checks_positive(self) -> None:
        test_schema = self.__schema
        staging_schema = self.__schema
        source_view = "vw_fact_vmc_utilization_cpu_mem_every5min_daily_check_positive"
        target_table = "dw_fact_vmc_utilization_cpu_mem_every5min_daily_check_positive"
        expect_table = "ex_fact_vmc_utilization_cpu_mem_every5min_daily_check_positive"

        res = self.__fact_insert_template_execute(
            test_schema,
            source_view,
            target_table,
            expect_table,
            "use_positive_check",
            staging_schema,
        )

        cli_assert(not res.exception, res)
        actual_rs = self.__trino_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self.__trino_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def test_insert_checks_negative(self) -> None:
        test_schema = self.__schema
        staging_schema = self.__schema
        source_view = "vw_fact_vmc_utilization_cpu_mem_every5min_daily_check_negative"
        target_table = "dw_fact_vmc_utilization_cpu_mem_every5min_daily_check_negative"
        expect_table = "ex_fact_vmc_utilization_cpu_mem_every5min_daily_check_negative"

        res = self.__fact_insert_template_execute(
            test_schema,
            source_view,
            target_table,
            expect_table,
            "use_negative_check",
            staging_schema,
        )

        assert res.exception
        actual_rs = self.__trino_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self.__trino_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output
        assert actual_rs.output != expected_rs.output

    def test_insert_clean_staging(self) -> None:
        test_schema = self.__schema
        staging_schema = self.__schema
        source_view = "vw_fact_vmc_utilization_cpu_mem_every5min_daily_clean_staging"
        target_table = "dw_fact_vmc_utilization_cpu_mem_every5min_daily_clean_staging"
        expect_table = "ex_fact_vmc_utilization_cpu_mem_every5min_daily_clean_staging"

        res_first_exec = self.__fact_insert_template_execute(
            test_schema,
            source_view,
            target_table,
            expect_table,
            "use_positive_check",
            staging_schema,
        )

        staging_table_name = f"vdk_check_{test_schema}_{target_table}"
        first_exec_rs = self.__trino_query(
            f"SELECT * FROM {staging_schema}.{staging_table_name}"
        )
        cli_assert_equal(0, res_first_exec)

        res_second_exec = self.__fact_insert_template_execute(
            test_schema,
            source_view,
            target_table,
            expect_table,
            "use_positive_check",
            staging_schema,
        )

        cli_assert_equal(0, res_second_exec)

        second_exec_rs = self.__trino_query(
            f"SELECT * FROM {staging_schema}.{staging_table_name}"
        )
        first_exec = {x for x in first_exec_rs.output.split("\n")}
        second_exec = {x for x in second_exec_rs.output.split("\n")}

        self.assertSetEqual(
            first_exec,
            second_exec,
            f"Clean up of staging table - {staging_table_name} is not made properly. Different data was found in the table after consecutive executions.",
        )

    def test_scd_upsert(self) -> None:
        test_schema = self.__schema
        source_view = "vw_dim_test_scd_upsert"
        target_table = "dw_dim_test_scd_upsert"
        expect_table = "ex_dim_test_scd_upsert"
        id_column = "org_id"

        res = self.__scd_upsert_execute(
            test_schema, source_view, target_table, expect_table, id_column
        )

        cli_assert(not res.exception, res)

        actual_rs = self.__trino_query(f"SELECT * FROM {test_schema}.{target_table}")
        expected_rs = self.__trino_query(f"SELECT * FROM {test_schema}.{expect_table}")
        assert actual_rs.output and expected_rs.output

        actual = {x for x in actual_rs.output.split("\n")}
        expected = {x for x in expected_rs.output.split("\n")}

        self.assertSetEqual(
            actual, expected, f"Elements in {expect_table} and {target_table} differ."
        )

    def __scd_upsert_execute(
        self,
        test_schema,
        source_view,
        target_table,
        expect_table,
        id_column,
        check=False,
        staging_schema=None,
    ):
        if check != False and staging_schema is not None:
            return self.__runner.invoke(
                [
                    "run",
                    get_test_job_path(
                        pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                        "load_dimension_scd1_upsert_template_job",
                    ),
                    "--arguments",
                    json.dumps(
                        {
                            "source_schema": test_schema,
                            "source_view": source_view,
                            "target_schema": test_schema,
                            "target_table": target_table,
                            "expect_schema": test_schema,
                            "expect_table": expect_table,
                            "id_column": id_column,
                            "check": check,
                            "staging_schema": staging_schema,
                        }
                    ),
                ]
            )
        else:
            return self.__runner.invoke(
                [
                    "run",
                    get_test_job_path(
                        pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                        "load_dimension_scd1_upsert_template_job",
                    ),
                    "--arguments",
                    json.dumps(
                        {
                            "source_schema": test_schema,
                            "source_view": source_view,
                            "target_schema": test_schema,
                            "target_table": target_table,
                            "expect_schema": test_schema,
                            "expect_table": expect_table,
                            "id_column": id_column,
                        }
                    ),
                ]
            )

    def __fact_insert_template_execute(
        self,
        test_schema,
        source_view,
        target_table,
        expect_table,
        check=False,
        staging_schema=None,
    ):
        if check != False and staging_schema is not None:
            return self.__runner.invoke(
                [
                    "run",
                    get_test_job_path(
                        pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                        "insert_template_job",
                    ),
                    "--arguments",
                    json.dumps(
                        {
                            "source_schema": test_schema,
                            "source_view": source_view,
                            "target_schema": test_schema,
                            "target_table": target_table,
                            "expect_schema": test_schema,
                            "expect_table": expect_table,
                            "check": check,
                            "staging_schema": staging_schema,
                        }
                    ),
                ]
            )
        else:
            return self.__runner.invoke(
                [
                    "run",
                    get_test_job_path(
                        pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                        "insert_template_job",
                    ),
                    "--arguments",
                    json.dumps(
                        {
                            "source_schema": test_schema,
                            "source_view": source_view,
                            "target_schema": test_schema,
                            "target_table": target_table,
                            "expect_schema": test_schema,
                            "expect_table": expect_table,
                        }
                    ),
                ]
            )

    def __template_table_exists(self, schema_name, target_name) -> Result:
        return self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"DESCRIBE {schema_name}.{target_name}",
            ]
        )

    def __trino_query(self, query: str) -> Result:
        return self.__runner.invoke(
            [
                "trino-query",
                "--query",
                query,
            ]
        )
