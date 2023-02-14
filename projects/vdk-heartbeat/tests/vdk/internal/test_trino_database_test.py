# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from unittest.mock import MagicMock

from vdk.internal.heartbeat.trino_database_test import TrinoDatabaseRunTest


def test_create_table():
    db = "my_db"
    table_name = "my_table"
    columns = {
        "int_column": int,
        "string_column": str,
        "bool_column": bool,
        "date_column": datetime,
        "float_column": float,
    }

    queries = []
    trino_test = TrinoDatabaseRunTest(MagicMock())
    trino_test._execute_query = lambda q: queries.append(q)

    trino_test._create_table(db, table_name, columns)

    assert len(queries) > 0
    expected = f"""
        CREATE TABLE IF NOT EXISTS my_db.my_table(
            int_column bigint,string_column varchar,bool_column boolean,date_column timestamp,float_column double
        )
        """
    assert queries[0] == expected


def test_delete_table():
    db = "my_db"
    table_name = "my_table"

    queries = []
    trino_test = TrinoDatabaseRunTest(MagicMock())
    trino_test._execute_query = lambda q: queries.append(q)

    trino_test._delete_table(db, table_name)

    expected = f"drop table if exists my_db.my_table"
    assert queries[0] == expected


def test_insert_table_row():
    db = "my_db"
    table_name = "my_table"
    row = {
        "int_col": 1,
        "str_col": "str",
        "float_col": 3.14,
        "bool_col": True,
        "date_col": datetime.fromisoformat("2012-10-10"),
    }

    queries = []
    trino_test = TrinoDatabaseRunTest(MagicMock())
    trino_test._execute_query = lambda q: queries.append(q)

    trino_test._insert_table_row(db, table_name, row)

    expected = (
        "INSERT INTO my_db.my_table (int_col,str_col,float_col,bool_col,date_col) values "
        "(1,'str',3.14,True,TIMESTAMP '2012-10-10 00:00:00.000')"
    )
    assert queries[0] == expected


def test_select_data():
    db = "my_db"
    table_name = "my_table"
    column_filters = {
        "int_column": 1,
        "string_column": "str",
        "bool_column": False,
        "date_column": datetime.fromisoformat("2012-10-10"),
        "float_column": 6.02214076,
    }

    queries = []
    trino_test = TrinoDatabaseRunTest(MagicMock())
    trino_test._execute_query = lambda q: queries.append(q)

    trino_test._select_data(db, table_name, column_filters)

    assert len(queries) > 0
    expected = (
        "select * from my_db.my_table where "
        "int_column=1 and string_column='str' and "
        "bool_column=False and date_column=TIMESTAMP '2012-10-10 00:00:00.000' and "
        "float_column=6.02214076"
    )
    assert queries[0] == expected
