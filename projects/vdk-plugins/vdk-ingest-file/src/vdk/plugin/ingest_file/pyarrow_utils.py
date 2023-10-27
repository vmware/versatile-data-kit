# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from typing import Dict
from typing import List
from typing import Type

import pyarrow


def python_types_to_pyarrow_schema(table_columns: dict):
    """
    Builds the pyarrow schema based on the column types and order in the target table, in order to ensure the new file
    will be compatible with the table
    """
    python_type_to_pyarrow_type_map = {
        str: pyarrow.string(),
        bool: pyarrow.bool_(),
        float: pyarrow.float64(),
        int: pyarrow.int64(),
        datetime: pyarrow.timestamp("ns"),
    }

    pyarrow_schema = []
    for column_name, column_type in table_columns.items():
        pyarrow_schema.append(
            (column_name, python_type_to_pyarrow_type_map[column_type])
        )
    return pyarrow.schema(pyarrow_schema)


def infer_column_types(payload: List[dict]) -> Dict[str, Type]:
    column_names = {}
    for row in payload:
        for key, value in row.items():
            if key not in column_names:
                column_names[key] = None

            if value is not None and column_names[key] is None:
                column_names[key] = type(value)

    for k, v in column_names.items():
        if v is None:
            column_names[k] = type(str)

    return column_names
