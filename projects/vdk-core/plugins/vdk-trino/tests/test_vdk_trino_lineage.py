# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import re
from unittest import mock

from click.testing import Result
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk import trino_plugin
from taurus.vdk.lineage import LineageLogger
from taurus.vdk.test_utils.util_funcs import CliEntryBasedTestRunner
from taurus.vdk.trino_plugin import LINEAGE_LOGGER_KEY

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"


@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
def test_lineage():
    mock_lineage = mock.MagicMock(LineageLogger)

    class TestConfigPlugin:
        @hookimpl
        def vdk_initialize(self, context):
            context.state.set(LINEAGE_LOGGER_KEY, mock_lineage)

    runner = CliEntryBasedTestRunner(TestConfigPlugin(), trino_plugin)

    result: Result = runner.invoke(["trino-query", "--query", "SELECT 1"])

    class LineageDataMatch:  # the lineage data is different on every run of the test,
        # so we need this class to generalize the dict which is to be matched
        def __eq__(self, lineage_data):
            return (
                lineage_data.keys() == {"@type", "query", "@id", "status"}
                and lineage_data["@type"] == "taurus_query"
                and lineage_data["status"] == "OK"
                and lineage_data["query"] == "SELECT 1"
                and re.fullmatch(r"[0-9]{10}\.[0-9]+", lineage_data["@id"])
            )

    mock_lineage.send.assert_called_with(LineageDataMatch())
