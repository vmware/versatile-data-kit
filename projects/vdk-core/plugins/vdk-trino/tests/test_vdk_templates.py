# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
import unittest
from unittest import mock

from click.testing import Result
from taurus.vdk import trino_plugin
from taurus.vdk.test_utils.util_funcs import cli_assert_equal
from taurus.vdk.test_utils.util_funcs import CliEntryBasedTestRunner
from taurus.vdk.test_utils.util_funcs import get_test_job_path
from taurus.vdk.trino_utils import TrinoQueries

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"
VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY = (
    "VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY"
)

org_move_data_to_table = TrinoQueries.move_data_to_table


def trino_move_data_to_table_break_tmp_to_target(
    obj, from_db: str, from_table_name: str, to_db: str, to_table_name: str
):
    if from_table_name == "tmp_dw_scmdb_people" and to_table_name == "dw_scmdb_people":
        obj.drop_table(from_db, from_table_name)
    return org_move_data_to_table(obj, from_db, from_table_name, to_db, to_table_name)


def trino_move_data_to_table_break_tmp_to_target_and_restore(
    obj, from_db: str, from_table_name: str, to_db: str, to_table_name: str
):
    if from_table_name == "tmp_dw_scmdb_people" and to_table_name == "dw_scmdb_people":
        obj.drop_table(from_db, from_table_name)
    if (
        from_table_name == "backup_dw_scmdb_people"
        and to_table_name == "dw_scmdb_people"
    ):
        obj.drop_table(from_db, from_table_name)
    return org_move_data_to_table(obj, from_db, from_table_name, to_db, to_table_name)


@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
        VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY: "INSERT_SELECT",
    },
)
class TemplateRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(trino_plugin)

    def test_scd1_template(self) -> None:
        source_schema = "default"
        source_view = "vw_dim_org"
        target_schema = "default"
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

        actual_rs: Result = self.__runner.invoke(
            ["trino-query", "--query", f"SELECT * FROM {target_schema}.{target_table}"]
        )

        expected_rs: Result = self.__runner.invoke(
            ["trino-query", "--query", f"SELECT * FROM {source_schema}.{source_view}"]
        )

        cli_assert_equal(0, actual_rs)
        cli_assert_equal(0, expected_rs)
        assert (
            actual_rs.output == expected_rs.output
        ), f"Elements in {source_view} and {target_table} differ."

    def test_scd2_template(self) -> None:
        test_schema = "default"
        source_view = "vw_scmdb_people"
        target_table = "dw_scmdb_people"
        expect_table = "ex_scmdb_people"

        result: Result = self.__scd2_template_execute(
            test_schema, source_view, target_table, expect_table
        )
        cli_assert_equal(0, result)

        # Check if we got the expected result and successfully dropped backup
        self.__scd2_template_check_expected_res(test_schema, target_table, expect_table)
        cli_assert_equal(
            1, self.__template_table_exists(test_schema, "backup_" + target_table)
        )

    def test_scd2_template_restore_target_from_backup_on_start(self) -> None:
        test_schema = "default"
        source_view = "vw_scmdb_people"
        target_table = "dw_scmdb_people"
        expect_table = "ex_scmdb_people"

        result: Result = self.__scd2_template_execute(
            test_schema, source_view, target_table, expect_table, "restore_from_backup"
        )
        cli_assert_equal(0, result)

        self.__scd2_template_check_expected_res(test_schema, target_table, expect_table)

    @mock.patch.object(
        TrinoQueries,
        "move_data_to_table",
        new=trino_move_data_to_table_break_tmp_to_target,
    )
    def test_scd2_template_fail_last_step_and_restore_target(self):
        test_schema = "default"
        source_view = "vw_scmdb_people"
        target_table = "dw_scmdb_people"
        expect_table = "ex_scmdb_people"

        result: Result = self.__scd2_template_execute(
            test_schema, source_view, target_table, expect_table
        )

        # Check if template fails but target is successfully restored
        cli_assert_equal(1, result)
        cli_assert_equal(0, self.__template_table_exists(test_schema, target_table))

    @mock.patch.object(
        TrinoQueries,
        "move_data_to_table",
        new=trino_move_data_to_table_break_tmp_to_target_and_restore,
    )
    def test_scd2_template_fail_last_step_and_fail_restore_target(self):
        test_schema = "default"
        source_view = "vw_scmdb_people"
        target_table = "dw_scmdb_people"
        expect_table = "ex_scmdb_people"

        result: Result = self.__scd2_template_execute(
            test_schema, source_view, target_table, expect_table
        )

        # Check if template fails and target fails to be restored
        cli_assert_equal(1, result)
        cli_assert_equal(1, self.__template_table_exists(test_schema, target_table))

        assert (
            f"Table {test_schema}.{target_table} is lost!" in result.output
        ), "Missing log for losing target schema."

    def __scd2_template_execute(
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
                    "load_dimension_scd2_template_job",
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
                        "id_column": "sddc_id",
                        "sk_column": "sddc_sk",
                        "value_columns": [
                            "updated_by_user_id",
                            "state",
                            "is_next",
                            "cloud_vendor",
                            "version",
                        ],
                        "tracked_columns": [
                            "updated_by_user_id",
                            "state",
                            "is_next",
                            "version",
                        ],
                        "active_from_column": "active_from",
                        "active_to_column": "active_to",
                        "active_to_max_value": "9999-12-31",
                        "updated_at_column": "updated_at",
                        "start_time_column": "start_time",
                        "end_time_column": "end_time",
                        "end_time_default_value": "9999-12-31",
                        "test_restore_from_backup": f"{restore_from_backup}",
                    }
                ),
            ]
        )

    def __scd2_template_check_expected_res(
        self, test_schema, target_table, expect_table
    ) -> None:
        # don't check first (surrogate key) column from the two results,
        # as those are uniquely generated and might differ

        actual_rs: Result = self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"""SELECT active_from, active_to, sddc_id, updated_by_user_id, state, is_next, cloud_vendor, version
                FROM {test_schema}.{target_table}
                ORDER BY sddc_id, active_to""",
            ]
        )

        expected_rs: Result = self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"""SELECT active_from, active_to, sddc_id, updated_by_user_id, state, is_next, cloud_vendor, version
                FROM {test_schema}.{expect_table}
                ORDER BY sddc_id, active_to""",
            ]
        )

        cli_assert_equal(0, actual_rs)
        cli_assert_equal(0, expected_rs)
        assert (
            actual_rs.output == expected_rs.output
        ), f"Elements in {target_table} and {expect_table} differ."

    def __template_table_exists(self, schema_name, target_name) -> Result:
        return self.__runner.invoke(
            [
                "trino-query",
                "--query",
                f"DESCRIBE {schema_name}.{target_name}",
            ]
        )


@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
        VDK_TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY: "RENAME",
    },
)
class TemplateRegressionTestsRenameStrategy(TemplateRegressionTests):
    pass
