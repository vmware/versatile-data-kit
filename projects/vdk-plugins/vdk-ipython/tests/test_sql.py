# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from unittest.mock import patch

import ipyaggrid

_log = logging.getLogger(__name__)


@patch.dict(os.environ, {"USE_DEFAULT_CELL_TABLE_OUTPUT": "true"})
def test_simple_select(ip, capsys):
    query = """
    %%vdksql
    select 1 as one, 2 as two
    """
    ip.get_ipython().run_cell(query)
    expected_out = "   one  two\n0    1    2"
    assert expected_out in capsys.readouterr().out


def test_simple_select_with_ipyaggrid(ip, capsys):
    query = """
    %%vdksql
    select 1 as one, 2 as two
    """
    result: ipyaggrid.Grid = ip.get_ipython().run_cell(query).result
    assert isinstance(result, ipyaggrid.Grid)
    assert result.grid_data_in.values.tolist() == [[1, 2]]


@patch.dict(os.environ, {"USE_DEFAULT_CELL_TABLE_OUTPUT": "true"})
def test_auto_vdk_initialize(session_ip, capsys):
    query = """
    %%vdksql
    select 1 as one, 2 as two
    """
    try:
        session_ip.run_line_magic(magic_name="load_ext", line="vdk.plugin.ipython")
        capsys.readouterr()  # reset
        session_ip.get_ipython().run_cell(query)
        expected_out = "   one  two\n0    1    2"
        assert expected_out in capsys.readouterr().out
    finally:
        session_ip.run_line_magic(magic_name="reset", line="-f")


@patch.dict(os.environ, {"USE_DEFAULT_CELL_TABLE_OUTPUT": "true"})
def test_create_insert(sqlite_ip, tmpdir):
    sqlite_ip.run_cell_magic(
        magic_name="vdksql",
        line="",
        cell="CREATE TABLE stocks (date text, symbol text, price real)",
    )

    sqlite_ip.run_cell_magic(
        magic_name="vdksql",
        line="",
        cell="""INSERT INTO stocks
                      VALUES ('2020-01-01', 'GOOG', 123.0), ('2021-01-01', 'GOOG', 123.0)""",
    )
    assert "date        symbol      price" in (
        sqlite_ip.get_ipython().getoutput(
            "! " "vdk " "sqlite-query -q 'SELECT * FROM stocks'"
        )
    )
    assert "2020-01-01  GOOG          123" in (
        sqlite_ip.get_ipython().getoutput(
            "! " "vdk " "sqlite-query -q 'SELECT * FROM stocks'"
        )
    )
    assert "2021-01-01  GOOG          123" in (
        sqlite_ip.get_ipython().getoutput(
            "! " "vdk " "sqlite-query -q 'SELECT * FROM stocks'"
        )
    )


@patch.dict(os.environ, {"USE_DEFAULT_CELL_TABLE_OUTPUT": "true"})
def test_complex_usecase(sqlite_ip, capsys):
    sqlite_ip.get_ipython().run_cell(
        "%env INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND=true"
    )

    create_query = """
    %%vdksql
    -- comments in query
    -- create table stocks_before (date text)
    create table stocks(
        date text,
        symbol text,
        price real
    )
    -- another comment
    """
    assert (
        sqlite_ip.get_ipython().run_cell(create_query).result
        == "Query statement executed successfully."
    )

    ingest_cell = """
    job_input = VDK.get_initialized_job_input()
    payload=dict(date="2020-01-01", symbol="GOOG", price=123)
    job_input.send_object_for_ingestion(payload=payload, destination_table="stocks")
    payload=dict(date="2020-01-02", symbol="GOOG", price=456)
    job_input.send_object_for_ingestion(payload=payload, destination_table="stocks")
    """
    sqlite_ip.get_ipython().run_cell(ingest_cell)

    select_query = """
    %%vdksql
    SELECT *
    FROM stocks
    ORDER BY date ASC
    """
    capsys.readouterr()  # reset buffer
    select_output = sqlite_ip.get_ipython().run_cell(select_query).result
    assert select_output.values.tolist() == [
        ["2020-01-01", "GOOG", 123.0],
        ["2020-01-02", "GOOG", 456.0],
    ]
    expected_out = (
        "         date symbol  price\n"
        "0  2020-01-01   GOOG  123.0\n"
        "1  2020-01-02   GOOG  456.0\n"
    )
    assert expected_out in capsys.readouterr().out


@patch.dict(os.environ, {"USE_DEFAULT_CELL_TABLE_OUTPUT": "true"})
def test_syntax_error(sqlite_ip, capsys):
    broken_query = """
    %%vdksql
    create_is_misspelled table stocks(
        date text
    )
    """
    sqlite_ip.get_ipython().run_cell(broken_query)
    assert '"create_is_misspelled": syntax error' in capsys.readouterr().err
