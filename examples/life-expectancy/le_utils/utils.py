# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import math

import numpy as np


def build_insert_query(row, cols, output_table):
    """
    Build an formatted query for insertion.

    Keyword arguments:
    -- row (pandas.Series) the list of values to be inserted in the query
    -- cols (list) the list of columns name of the SQL table

    Return:
    -- query (string) a string containing the insert statement

    """
    values = ""
    keys = cols.copy()
    for index in range(0, len(row)):

        # manage NaN values, both for strings and numeric values
        if (row[index] != row[index]) and (math.isnan(row[index])):
            # do not insert  NaN values, thus remove it from columns
            keys.remove(cols[index])

        else:
            # quote only strings and convert numeric values to strings
            if isinstance(row[index], str):
                values = values + ", '" + row[index] + "'"
            else:
                values = values + ", " + str(row[index])

    # remove the first comma
    values = values[1:]

    cols = ", ".join([str(i) for i in keys])
    return f"INSERT INTO {output_table} ({cols}) VALUES ({values})"
