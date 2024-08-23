# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from decimal import Decimal
from unittest import mock
from unittest import TestCase

import pytest
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path
from vdk.plugin.trino import trino_plugin
from vdk.plugin.trino.trino_config import TrinoConfiguration
from vdk.plugin.trino.trino_connection import TrinoConnection

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"
VDK_LOG_EXECUTION_RESULT = "VDK_LOG_EXECUTION_RESULT"


# these are for the default database
@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
        VDK_INGEST_METHOD_DEFAULT: "TRINO",
        VDK_LOG_EXECUTION_RESULT: "True",
    },
)
class IngestToTrinoTests(TestCase):
    def test_ingest_to_multiple_trino(self):
        runner = CliEntryBasedTestRunner(trino_plugin)

        ingest_job_result = runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "test_ingest_to_trino_multiple_db",
                ),
            ]
        )

        cli_assert_equal(0, ingest_job_result)

        # check default db

        check_result = runner.invoke(
            ["trino-query", "--query", "SELECT * FROM test_table"]
        )

        assert check_result.stdout == (
            "------  --  ---  ----  ---\n"
            "string  12  1.2  True  3.2\n"
            "------  --  ---  ----  ---\n"
        )

        # check secondary db
        builder = ConfigurationBuilder()
        builder.add("TRINO_HOST", "localhost")
        builder.add("TRINO_PORT", 8081)
        builder.add("TRINO_SCHEMA", "default")
        builder.add("TRINO_CATALOG", "memory")
        builder.add("TRINO_USER", "unknown")
        builder.add("TRINO_PASSWORD", None)
        builder.add("TRINO_USE_SSL", False)
        builder.add("TRINO_SSL_VERIFY", True)
        builder.add("TRINO_TIMEOUT_SECONDS", None)
        cfg = builder.build()

        trino_conf = TrinoConfiguration(cfg)
        conn = TrinoConnection(
            configuration=trino_conf,
            section=None,
            lineage_logger=None,
        )

        result = conn.execute_query("SELECT * FROM secondary_test_table")

        assert result == [["string", 13, 1.2, False, Decimal("3.20")]]
