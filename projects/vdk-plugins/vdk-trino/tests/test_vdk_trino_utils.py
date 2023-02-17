# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
import unittest
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path
from vdk.plugin.trino import trino_plugin
from vdk.plugin.trino.trino_utils import TrinoTemplateQueries

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"


@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
class TrinoUtilsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(trino_plugin)

    def test_move_data_to_table_insert_select_strategy(self) -> None:
        with mock.patch.object(
            TrinoTemplateQueries,
            "get_move_data_to_table_strategy",
            return_value="INSERT_SELECT",
        ) as patched:
            self.check_move_data_to_table_for_current_strategy()

    def test_move_data_to_table_rename_strategy(self) -> None:
        with mock.patch.object(
            TrinoTemplateQueries,
            "get_move_data_to_table_strategy",
            return_value="RENAME",
        ) as patched:
            self.check_move_data_to_table_for_current_strategy()

    def test_move_data_to_table_invalid_strategy(self) -> None:
        with mock.patch.object(
            TrinoTemplateQueries,
            "get_move_data_to_table_strategy",
            return_value="INVALID_STRATEGY",
        ) as patched:
            with pytest.raises(Exception):
                self.check_move_data_to_table_for_current_strategy()

    def check_move_data_to_table_for_current_strategy(self) -> None:
        db = "default"
        src = "test_scr_t"
        target = "test_target_t"

        result: Result = self.__runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "test_move_data_strategy_job",
                ),
                "--arguments",
                json.dumps(
                    {
                        "db": db,
                        "src": src,
                        "target": target,
                    }
                ),
            ]
        )
        cli_assert_equal(0, result)
