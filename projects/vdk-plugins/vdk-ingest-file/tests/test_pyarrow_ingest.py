# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json

import pyarrow as pa
import pytest
from vdk.plugin.ingest_file.ingestion_to_arrow import IngestionToFile


def test_ingest_payload(tmpdir):
    # Initialize IngestionToFile object
    ingester = IngestionToFile()

    # Mock data
    payload = [
        {"column1": "value1", "column2": "value2"},
        {"column1": "value3", "column2": "value4"},
    ]
    destination_table = "test_table"
    target = str(tmpdir)

    # Call ingest_payload
    ingester.ingest_payload(payload, destination_table, target=target)

    # Asserts: You may need to adjust these based on what you want to assert.
    # For example, you can check if the files are created and have the correct data.
    assert len(tmpdir.listdir()) == 1
    for f in tmpdir.listdir():
        with pa.OSFile(f, "rb") as source:
            reader = pa.RecordBatchFileReader(source)
            table = reader.read_all()

        assert table.num_rows == 2
        assert table.column("column1")[0].as_py() == "value1"
        assert table.column("column1")[1].as_py() == "value3"
        assert table.column("column2")[0].as_py() == "value2"
        assert table.column("column2")[1].as_py() == "value4"
