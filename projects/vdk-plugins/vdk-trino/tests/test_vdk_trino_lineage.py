# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import re
import uuid
from unittest import mock

import pytest
from click.testing import Result
from vdk.api.plugin.hook_markers import hookimpl
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.trino import trino_plugin
from vdk.plugin.trino.lineage import LineageLogger
from vdk.plugin.trino.trino_plugin import LINEAGE_LOGGER_KEY

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
def test_lineage_for_insert():

    table_name = "test_table_" + uuid.uuid4().hex

    mock_lineage_logger = mock.MagicMock(LineageLogger)

    class TestConfigPlugin:
        @hookimpl
        def vdk_initialize(self, context):
            context.state.set(LINEAGE_LOGGER_KEY, mock_lineage_logger)

    runner = CliEntryBasedTestRunner(TestConfigPlugin(), trino_plugin)

    result: Result = runner.invoke(
        ["trino-query", "--query", f"create table {table_name} (test_column varchar)"]
    )
    cli_assert_equal(0, result)

    insert_query = f"insert into {table_name} values('test value')"
    result: Result = runner.invoke(["trino-query", "--query", insert_query])
    cli_assert_equal(0, result)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class InsertLineageDataMatch:
        def __eq__(self, lineage_data):
            import json

            print("INSERT query lineage data:")
            print(json.dumps(lineage_data, indent=4))
            return (
                lineage_data.keys()
                >= {"@type", "query", "@id", "status", "outputTable"}
                and lineage_data["@type"] == "insert"
                and lineage_data["status"] == "OK"
                and lineage_data["query"] == insert_query
                and re.fullmatch(r"[0-9]{10}\.[0-9]+", lineage_data["@id"])
                and lineage_data["outputTable"]["schemaTable"]["table"] == table_name
            )

    mock_lineage_logger.send.assert_called_with(InsertLineageDataMatch())


@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
def test_lineage_for_select():

    table_name = "test_table_" + uuid.uuid4().hex

    mock_lineage_logger = mock.MagicMock(LineageLogger)

    class TestConfigPlugin:
        @hookimpl
        def vdk_initialize(self, context):
            context.state.set(LINEAGE_LOGGER_KEY, mock_lineage_logger)

    runner = CliEntryBasedTestRunner(TestConfigPlugin(), trino_plugin)

    result: Result = runner.invoke(
        ["trino-query", "--query", f"create table {table_name} (test_column varchar)"]
    )
    cli_assert_equal(0, result)

    select_query = f"select * from {table_name}"
    result: Result = runner.invoke(["trino-query", "--query", select_query])
    cli_assert_equal(0, result)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class SelectLineageDataMatch:
        def __eq__(self, lineage_data):
            import json

            print("SELECT query lineage data:")
            print(json.dumps(lineage_data, indent=4))
            return (
                lineage_data.keys()
                >= {"@type", "query", "@id", "status", "inputTableColumnInfos"}
                and lineage_data["@type"] == "select"
                and lineage_data["status"] == "OK"
                and lineage_data["query"] == select_query
                and re.fullmatch(r"[0-9]{10}\.[0-9]+", lineage_data["@id"])
                and lineage_data["inputTableColumnInfos"][0]["table"]["schemaTable"][
                    "table"
                ]
                == table_name
            )

    mock_lineage_logger.send.assert_called_with(SelectLineageDataMatch())


@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
def test_lineage_for_insert_select():
    table_name_from = "test_table_" + uuid.uuid4().hex
    table_name_to = "test_table_" + uuid.uuid4().hex

    mock_lineage_logger = mock.MagicMock(LineageLogger)

    class TestConfigPlugin:
        @hookimpl
        def vdk_initialize(self, context):
            context.state.set(LINEAGE_LOGGER_KEY, mock_lineage_logger)

    runner = CliEntryBasedTestRunner(TestConfigPlugin(), trino_plugin)

    result: Result = runner.invoke(
        [
            "trino-query",
            "--query",
            f"create table {table_name_from} (test_column varchar)",
        ]
    )
    cli_assert_equal(0, result)

    result: Result = runner.invoke(
        [
            "trino-query",
            "--query",
            f"create table {table_name_to} (test_column varchar)",
        ]
    )
    cli_assert_equal(0, result)

    insert_select_query = f"insert into {table_name_to} select * from {table_name_from}"
    result: Result = runner.invoke(["trino-query", "--query", insert_select_query])
    cli_assert_equal(0, result)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class InsertSelectLineageDataMatch:
        def __eq__(self, lineage_data):
            import json

            print("INSERT..SELECT query lineage data:")
            print(json.dumps(lineage_data, indent=4))
            return (
                lineage_data.keys()
                >= {"@type", "query", "@id", "status", "inputTableColumnInfos"}
                and lineage_data["@type"] == "insert_select"
                and lineage_data["status"] == "OK"
                and lineage_data["query"] == insert_select_query
                and re.fullmatch(r"[0-9]{10}\.[0-9]+", lineage_data["@id"])
                and lineage_data["inputTableColumnInfos"][0]["table"]["schemaTable"][
                    "table"
                ]
                == table_name_from
                and lineage_data["outputTable"]["schemaTable"]["table"] == table_name_to
            )

    mock_lineage_logger.send.assert_called_with(InsertSelectLineageDataMatch())


@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
def test_lineage_for_rename_table():
    table_name_from = "test_table_" + uuid.uuid4().hex
    table_name_to = "test_table_" + uuid.uuid4().hex

    mock_lineage_logger = mock.MagicMock(LineageLogger)

    class TestConfigPlugin:
        @hookimpl
        def vdk_initialize(self, context):
            context.state.set(LINEAGE_LOGGER_KEY, mock_lineage_logger)

    runner = CliEntryBasedTestRunner(TestConfigPlugin(), trino_plugin)

    result: Result = runner.invoke(
        [
            "trino-query",
            "--query",
            f"create table {table_name_from} (test_column varchar)",
        ]
    )
    cli_assert_equal(0, result)

    rename_query = f"alter table {table_name_from} rename to {table_name_to}"
    result: Result = runner.invoke(["trino-query", "--query", rename_query])
    cli_assert_equal(0, result)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class RenameTableLineageDataMatch:
        def __eq__(self, lineage_data):
            import json

            print("RENAME TABLE query lineage data:")
            print(json.dumps(lineage_data, indent=4))
            return (
                lineage_data.keys()
                >= {"@type", "query", "@id", "status", "table_from", "table_to"}
                and lineage_data["@type"] == "rename_table"
                and lineage_data["status"] == "OK"
                and lineage_data["query"] == rename_query
                and re.fullmatch(r"[0-9]{10}\.[0-9]+", lineage_data["@id"])
                and lineage_data["table_from"] == table_name_from
                and lineage_data["table_to"] == table_name_to
            )

    mock_lineage_logger.send.assert_called_with(RenameTableLineageDataMatch())
