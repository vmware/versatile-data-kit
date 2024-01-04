# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.impala import impala_plugin
from vdk.plugin.oracle import oracle_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


def test_plugin_clash():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOG_EXECUTION_RESULT": "True",
            "VDK_ORACLE_THICK_MODE": "False",
            "VDK_INGEST_METHOD_DEFAULT": "ORACLE",
            "VDK_ORACLE_USER": "ADMIN",
            "VDK_ORACLE_PASSWORD": "Gr0mh3llscr3am",
            "VDK_ORACLE_CONNECTION_STRING": "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=ge975b87ba26804_newdb_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))",
            "DB_DEFAULT_TYPE": "oracle",
            "VDK_IMPALA_SYNC_DDL": "True",
        },
    ):
        runner = CliEntryBasedTestRunner(impala_plugin, oracle_plugin)
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-connect-execute-job")]
        )
        cli_assert_equal(0, result)
