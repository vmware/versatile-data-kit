# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from contextlib import contextmanager
from typing import Optional

from vdk.api.lineage.model.sql.model import LineageData
from vdk.api.lineage.model.sql.model import LineageTable

log = logging.getLogger(__name__)


@contextmanager
def no_op_dict_config():
    """
    Hacky workaround to import sqllineage as it is overriding logging configuration in sqllineage.__init__
    It's likely because LineageRunner is considered private so we are a bit abusing the tool here.
    """
    import logging.config

    cached_dict_config = logging.config.dictConfig
    logging.config.dictConfig = lambda x: None
    try:
        yield
    finally:
        logging.config.dictConfig = cached_dict_config


with no_op_dict_config():
    from sqllineage.core.models import Table
    from sqllineage.runner import LineageRunner


def get_table_lineage_from_query(
    query: str, schema: Optional[str], catalog: Optional[str]
) -> LineageData:
    """
    This method parses the sql query. If and only if it is a rename table query,
    the method returns the names of the source and destination table.
    :param query: The SQL query potentially containing a RENAME TABLE operation
    :param schema: The schema which is queried
    :param catalog: The catalog which is queried
    :return: A tuple with (table_from, table_to) if it is a RENAME TABLE query, None otherwise.
    """

    runner = LineageRunner(query)

    if len(runner.statements()) == 0:
        # log.debug("No statement passed")
        return None

    if len(runner.statements()) > 1:
        raise RuntimeError(
            "Query with more than one statement is passed. "
            "Make sure that multiple query statements (separated) are not passed to this method."
            f"Query passed is '{query}' "
        )

    input_tables = [
        _lineage_table_from_name(source_table, schema, catalog)
        for source_table in runner.source_tables
    ]
    output_table = None
    if len(runner.target_tables) == 1:
        output_table = _lineage_table_from_name(
            runner.target_tables[0], schema, catalog
        )
    elif len(runner.target_tables) > 1:
        raise RuntimeError(
            "Query with more than one target table should not be possible. "
            "Make sure that multiple queries (separated) are not passed accidentally."
            f"Query is '{query}' "
        )

    return LineageData(
        query=query,
        query_type="not implemented",
        query_status="",
        input_tables=input_tables,
        output_table=output_table,
    )


def _lineage_table_from_name(
    table: Table, default_schema: str, default_catalog: str
) -> LineageTable:
    tokens = []
    if table.schema:
        tokens = table.schema.raw_name.split(".")

    if len(tokens) == 0:
        return LineageTable(default_catalog, default_schema, table.raw_name)
    elif len(tokens) == 1:
        return LineageTable(default_catalog, tokens[0], table.raw_name)
    elif len(tokens) == 2:
        return LineageTable(tokens[0], tokens[1], table.raw_name)
    else:
        return None
