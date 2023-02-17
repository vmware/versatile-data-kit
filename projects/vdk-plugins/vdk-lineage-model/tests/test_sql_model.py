# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.lineage.model.sql.model import LineageTable


def test_lineage_table_str():
    assert (
        str(LineageTable(catalog="catalog", schema="schema", table="table"))
        == "catalog.schema.table"
    )
