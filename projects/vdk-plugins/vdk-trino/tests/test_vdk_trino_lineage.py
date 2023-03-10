# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import uuid
from unittest import mock

import pytest
from click.testing import Result
from vdk.api.lineage.model.logger.lineage_logger import ILineageLogger
from vdk.api.lineage.model.sql.model import LineageData
from vdk.api.plugin.hook_markers import hookimpl
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.trino import trino_plugin
from vdk.plugin.trino.trino_plugin import LINEAGE_LOGGER_KEY

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"


class TestConfigPlugin:
    def __init__(self, lineage_logger: ILineageLogger):
        self.lineage_logger = lineage_logger

    @hookimpl
    def vdk_initialize(self, context):
        context.state.set(LINEAGE_LOGGER_KEY, self.lineage_logger)


def execute_query(runner, query: str):
    result: Result = runner.invoke(["trino-query", "--query", query])
    cli_assert_equal(0, result)


@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
def test_lineage_not_collected_for_heartbeat_query():
    mock_lineage_logger = mock.MagicMock(ILineageLogger)
    runner = CliEntryBasedTestRunner(
        TestConfigPlugin(mock_lineage_logger), trino_plugin
    )
    execute_query(runner, "select 1")
    assert not mock_lineage_logger.send.called


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

    mock_lineage_logger = mock.MagicMock(ILineageLogger)
    runner = CliEntryBasedTestRunner(
        TestConfigPlugin(mock_lineage_logger), trino_plugin
    )

    execute_query(runner, f"create table {table_name} (test_column varchar)")

    insert_query = f"insert into {table_name} values('test value')"
    execute_query(runner, insert_query)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class InsertLineageDataMatcher:
        def __eq__(self, lineage_data: LineageData):
            assert lineage_data.query == insert_query
            assert lineage_data.query_type == "insert"
            assert lineage_data.query_status == "OK"
            assert lineage_data.output_table.catalog == "memory"
            assert lineage_data.output_table.schema == "default"
            assert lineage_data.output_table.table == table_name
            return True

    mock_lineage_logger.send.assert_called_with(InsertLineageDataMatcher())


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

    mock_lineage_logger = mock.MagicMock(ILineageLogger)
    runner = CliEntryBasedTestRunner(
        TestConfigPlugin(mock_lineage_logger), trino_plugin
    )

    execute_query(runner, f"create table {table_name} (test_column varchar)")

    select_query = f"select * from {table_name}"
    execute_query(runner, select_query)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class SelectLineageDataMatcher:
        def __eq__(self, lineage_data: LineageData):
            assert lineage_data.query == select_query
            assert lineage_data.query_type == "select"
            assert lineage_data.query_status == "OK"
            assert len(lineage_data.input_tables) == 1
            assert lineage_data.input_tables[0].catalog == "memory"
            assert lineage_data.input_tables[0].schema == "default"
            assert lineage_data.input_tables[0].table == table_name
            return True

    mock_lineage_logger.send.assert_called_with(SelectLineageDataMatcher())


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
    table_name_source = "test_tbl_src_" + uuid.uuid4().hex
    table_name_dest = "test_tbl_dst_" + uuid.uuid4().hex

    mock_lineage_logger = mock.MagicMock(ILineageLogger)
    runner = CliEntryBasedTestRunner(
        TestConfigPlugin(mock_lineage_logger), trino_plugin
    )

    execute_query(runner, f"create table {table_name_source} (test_column varchar)")
    execute_query(runner, f"create table {table_name_dest} (test_column varchar)")

    insert_select_query = (
        f"insert into {table_name_dest} select * from {table_name_source}"
    )
    execute_query(runner, insert_select_query)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class InsertSelectLineageDataMatch:
        def __eq__(self, lineage_data: LineageData):
            assert lineage_data.query == insert_select_query
            assert lineage_data.query_type == "insert_select"
            assert lineage_data.query_status == "OK"
            assert lineage_data.input_tables[0].table == table_name_source
            assert lineage_data.output_table.table == table_name_dest
            return True

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
def test_lineage_for_insert_select_full_names():
    test_schema = "memory.test_schema"
    table_name_source = "test_tbl_src_" + uuid.uuid4().hex
    table_name_dest = "test_tbl_dst_" + uuid.uuid4().hex

    mock_lineage_logger = mock.MagicMock(ILineageLogger)
    runner = CliEntryBasedTestRunner(
        TestConfigPlugin(mock_lineage_logger), trino_plugin
    )

    execute_query(runner, f"create schema if not exists {test_schema}")
    execute_query(
        runner, f"create table {test_schema}.{table_name_source} (test_column varchar)"
    )
    execute_query(
        runner, f"create table {test_schema}.{table_name_dest} (test_column varchar)"
    )

    insert_select_query = f"insert into {test_schema}.{table_name_dest} select * from {test_schema}.{table_name_source}"
    execute_query(runner, insert_select_query)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class InsertSelectLineageDataMatch:
        def __eq__(self, lineage_data: LineageData):
            assert lineage_data.query == insert_select_query
            assert lineage_data.query_type == "insert_select"
            assert lineage_data.query_status == "OK"
            assert lineage_data.input_tables[0].catalog == "memory"
            assert lineage_data.input_tables[0].schema == "test_schema"
            assert lineage_data.input_tables[0].table == table_name_source
            assert lineage_data.output_table.catalog == "memory"
            assert lineage_data.output_table.schema == "test_schema"
            assert lineage_data.output_table.table == table_name_dest
            return True

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

    mock_lineage_logger = mock.MagicMock(ILineageLogger)
    runner = CliEntryBasedTestRunner(
        TestConfigPlugin(mock_lineage_logger), trino_plugin
    )

    execute_query(runner, f"create table {table_name_from} (test_column varchar)")

    rename_query = f"alter table {table_name_from} rename to {table_name_to}"
    execute_query(runner, rename_query)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class RenameTableLineageDataMatch:
        def __eq__(self, lineage_data: LineageData):
            assert lineage_data.query == rename_query
            assert lineage_data.query_type == "rename_table"
            assert lineage_data.query_status == "OK"
            assert lineage_data.input_tables[0].table == table_name_from
            assert lineage_data.output_table.table == table_name_to
            return True

    mock_lineage_logger.send.assert_called_with(RenameTableLineageDataMatch())


@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
def test_lineage_for_rename_table_full_names():
    test_schema = "memory.test_schema"
    table_name_from = "test_table_" + uuid.uuid4().hex
    table_name_to = "test_table_" + uuid.uuid4().hex

    mock_lineage_logger = mock.MagicMock(ILineageLogger)
    runner = CliEntryBasedTestRunner(
        TestConfigPlugin(mock_lineage_logger), trino_plugin
    )

    execute_query(runner, f"create schema if not exists {test_schema}")
    execute_query(
        runner, f"create table {test_schema}.{table_name_from} (test_column varchar)"
    )

    rename_query = f"alter table {test_schema}.{table_name_from} rename to {test_schema}.{table_name_to}"
    execute_query(runner, rename_query)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class RenameTableLineageDataMatch:
        def __eq__(self, lineage_data: LineageData):
            assert lineage_data.query == rename_query
            assert lineage_data.query_type == "rename_table"
            assert lineage_data.query_status == "OK"
            assert lineage_data.input_tables[0].catalog == "memory"
            assert lineage_data.input_tables[0].schema == "test_schema"
            assert lineage_data.input_tables[0].table == table_name_from
            assert lineage_data.output_table.catalog == "memory"
            assert lineage_data.output_table.schema == "test_schema"
            assert lineage_data.output_table.table == table_name_to
            return True

    mock_lineage_logger.send.assert_called_with(RenameTableLineageDataMatch())


@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
def test_lineage_for_rename_table_if_exists():
    table_name_from = "test_table_" + uuid.uuid4().hex
    table_name_to = "test_table_" + uuid.uuid4().hex

    mock_lineage_logger = mock.MagicMock(ILineageLogger)
    runner = CliEntryBasedTestRunner(
        TestConfigPlugin(mock_lineage_logger), trino_plugin
    )

    execute_query(runner, f"create table {table_name_from} (test_column varchar)")

    rename_query = (
        f"alter table if exists {table_name_from}    rename to {table_name_to}"
    )
    execute_query(runner, rename_query)

    # the lineage data is different on every run of the test,
    # so we need this class to generalize the dict which is to be matched
    class RenameTableLineageDataMatch:
        def __eq__(self, lineage_data: LineageData):
            assert lineage_data.query == rename_query
            assert lineage_data.query_type == "rename_table"
            assert lineage_data.query_status == "OK"
            assert lineage_data.input_tables[0].table == table_name_from
            assert lineage_data.output_table.table == table_name_to
            return True

    mock_lineage_logger.send.assert_called_with(RenameTableLineageDataMatch())


@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
def test_lineage_not_collected_for_some_queries():
    table_name = "test_table_" + uuid.uuid4().hex

    mock_lineage_logger = mock.MagicMock(ILineageLogger)
    runner = CliEntryBasedTestRunner(
        TestConfigPlugin(mock_lineage_logger), trino_plugin
    )

    execute_query(runner, f"create table {table_name} (test_column varchar)")

    execute_query(runner, f"describe {table_name}")
    assert not mock_lineage_logger.send.called
