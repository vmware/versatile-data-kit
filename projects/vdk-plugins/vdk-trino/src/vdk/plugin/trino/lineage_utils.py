# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Any
from typing import Dict


def parse_rename_table_names(query: str) -> tuple:
    """
    This method parses the sql query. If and only if it is a rename table query,
    the method returns the names of the source and destination table.
    :param query: The SQL query potentially containing a RENAME TABLE operation
    :return: A tuple with (table_from, table_to) if it is a RENAME TABLE query, None otherwise.
    """
    import sqlparse
    from sqlparse.tokens import Whitespace
    from sqlparse.sql import Identifier

    formatted_query = sqlparse.format(query, reindent=True, keyword_case="upper")
    statement = sqlparse.parse(formatted_query)[0]
    tokens = statement.tokens
    if (
        tokens[0].value == "ALTER"
        and tokens[1].ttype == Whitespace
        and tokens[2].value == "TABLE"
        and tokens[3].ttype == Whitespace
        and isinstance(tokens[4], Identifier)  # table_from
        and tokens[5].ttype == Whitespace
        and tokens[6].value == "RENAME"
        and tokens[7].ttype == Whitespace
        and tokens[8].value == "TO"
        and tokens[9].ttype == Whitespace
        and isinstance(tokens[10], Identifier)  # table_to
    ):
        table_from = tokens[4].value
        table_to = tokens[10].value
        return table_from, table_to
    else:
        return None


def determine_query_type_from_plan(lineage_data: Dict[str, Any]) -> str:
    has_input = (
        "inputTableColumnInfos" in lineage_data
        and len(lineage_data["inputTableColumnInfos"]) > 0
    )
    has_output = (
        "outputTable" in lineage_data and "schemaTable" in lineage_data["outputTable"]
    )
    if has_input and has_output:
        return "insert_select"
    elif has_input:
        return "select"
    elif has_output:
        return "insert"
    else:
        return "undefined"
