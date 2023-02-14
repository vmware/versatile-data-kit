# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.api.lineage.model.sql.model import LineageData
from vdk.api.lineage.model.sql.model import LineageTable


def is_heartbeat_query(query: str):
    import sqlparse
    from sqlparse.tokens import Whitespace

    formatted_query = sqlparse.format(query, reindent=True, keyword_case="upper")
    statement = sqlparse.parse(formatted_query)[0]
    tokens = statement.tokens
    return (
        len(tokens) == 3
        and tokens[0].value == "SELECT"
        and tokens[1].ttype == Whitespace
        and tokens[2].ttype[0] == "Literal"
    )


def get_rename_table_lineage_from_query(
    query: str, schema: str, catalog: str
) -> LineageData:
    """
    This method parses the sql query. If and only if it is a rename table query,
    the method returns the names of the source and destination table.
    :param query: The SQL query potentially containing a RENAME TABLE operation
    :param schema: The schema which is queried
    :param catalog: The catalog which is queried
    :return: A tuple with (table_from, table_to) if it is a RENAME TABLE query, None otherwise.
    """
    import sqlparse
    from sqlparse.tokens import Keyword

    formatted_query = sqlparse.format(query, reindent=True, keyword_case="upper")
    statement = sqlparse.parse(formatted_query)[0]
    keywords = filter(
        lambda token: token.ttype in [Keyword, Keyword.DDL], statement.tokens
    )
    keyword_values = list(map(lambda token: token.value, keywords))

    if keyword_values == ["ALTER", "TABLE", "RENAME", "TO"]:
        table_from = _lineage_table_from_name(
            statement.tokens[4].value, schema, catalog
        )
        table_to = _lineage_table_from_name(statement.tokens[10].value, schema, catalog)
    elif keyword_values == ["ALTER", "TABLE", "IF", "EXISTS", "RENAME", "TO"]:
        table_from = _lineage_table_from_name(
            statement.tokens[8].value, schema, catalog
        )
        table_to = _lineage_table_from_name(statement.tokens[14].value, schema, catalog)
    else:
        return None
    return LineageData(
        query=query,
        query_type="rename_table",
        query_status="OK",
        input_tables=[table_from],
        output_table=table_to,
    )


def _lineage_table_from_name(
    table_name: str, schema: str, catalog: str
) -> LineageTable:
    tokens = table_name.split(".")
    if len(tokens) == 1:
        return LineageTable(catalog, schema, tokens[0])
    elif len(tokens) == 2:
        return LineageTable(catalog, tokens[0], tokens[1])
    elif len(tokens) == 3:
        return LineageTable(tokens[0], tokens[1], tokens[2])
    else:
        return None


def get_lineage_data_from_io_explain(
    query: str, lineage_result_json_string: str
) -> LineageData:
    """
    Constructs a LineageData object from the result of a Trino query plan

    :param query:
        The query the lineage data will be created for
    :param lineage_result_json_string:
        The exact result of 'EXPLAIN (TYPE IO, FORMAT JSON)'.
        It is a str representation of the JSON response.
    """
    input_tables = None
    output_table = None
    import json

    data = json.loads(lineage_result_json_string)
    if "inputTableColumnInfos" in data and len(data["inputTableColumnInfos"]) > 0:
        input_tables = _get_input_tables_from_explain(data["inputTableColumnInfos"])
    if "outputTable" in data and "schemaTable" in data["outputTable"]:
        output_table = _get_lineage_table_from_plan(data["outputTable"])
    if input_tables and output_table:
        query_type = "insert_select"
    elif input_tables:
        query_type = "select"
    elif output_table:
        query_type = "insert"
    else:
        query_type = "undefined"

    return LineageData(
        query=query,
        query_type=query_type,
        query_status="OK",
        input_tables=input_tables,
        output_table=output_table,
    )


def _get_lineage_table_from_plan(table_dict: dict) -> LineageTable:
    return LineageTable(
        catalog=table_dict["catalog"],
        schema=table_dict["schemaTable"]["schema"],
        table=table_dict["schemaTable"]["table"],
    )


def _get_input_tables_from_explain(input_tables: list) -> List[LineageTable]:
    return list(
        map(_get_lineage_table_from_plan, map(lambda t: t["table"], input_tables))
    )
