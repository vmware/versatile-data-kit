# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from unittest.mock import patch

import ipyaggrid

_log = logging.getLogger(__name__)


@patch.dict(
    os.environ,
    {"USE_DEFAULT_CELL_TABLE_OUTPUT": "true"},
)
def test_ingest_cell(sqlite_ip, capsys):
    query = """%%vdkingest
    [sources]
    s1 = {name = "auto-generated-data"}

    [destinations]
    d1 = {method = "sqlite"}

    [[flows]]
    from="s1"
    to="d1"
    """
    sqlite_ip.get_ipython().run_cell(query)
    assert capsys.readouterr().out == "\n"

    select_query = """
    %%vdksql
    SELECT * from stream_0
    """
    capsys.readouterr()  # reset buffer
    select_output = sqlite_ip.get_ipython().run_cell(select_query).result
    assert select_output.values.tolist() == [
        [1, "Stream_0_Name_0", 0],
        [2, "Stream_0_Name_1", 0],
    ]
