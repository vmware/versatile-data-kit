# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import pyarrow as pa
from vdk.plugin.ingest_file.arrow_writer import ArrowWriter


def test_arrow_file_content(tmpdir):
    tmp_path = pathlib.Path(str(tmpdir))
    writer = ArrowWriter(directory_path=str(tmp_path))
    payload = [{"column1": 1, "column2": "data1"}, {"column1": 2, "column2": "data2"}]
    writer.add_payload(payload)

    writer.close()

    created_files = list(tmp_path.iterdir())
    assert len(created_files) == 1
    file_path = created_files[0]
    with pa.ipc.open_file(str(file_path)) as f:
        table = f.read_all()

    expected_schema = pa.schema([("column1", pa.int64()), ("column2", pa.string())])
    assert table.schema.equals(expected_schema)

    expected_data = pa.table({"column1": [1, 2], "column2": ["data1", "data2"]})
    assert table.equals(expected_data)


def test_add_payload(tmpdir):
    tmp_path = pathlib.Path(str(tmpdir))
    writer = ArrowWriter(directory_path=str(tmp_path))

    # Define the payload
    payload = [{"column1": 1, "column2": "data1"}, {"column1": 2, "column2": "data2"}]

    # Add payload
    writer.add_payload(payload)

    created_files = list(tmp_path.iterdir())
    assert len(created_files) > 0


def test_file_initialization(tmpdir):
    tmp_path = pathlib.Path(str(tmpdir))
    writer = ArrowWriter(directory_path=str(tmp_path))
    payload = [{"column1": 1, "column2": "data1"}]
    writer.add_payload(payload)

    # Inspect the created file
    created_files = list(tmp_path.iterdir())
    assert len(created_files) == 1


def test_file_rollover(tmpdir):
    tmp_path = pathlib.Path(str(tmpdir))
    writer = ArrowWriter(directory_path=str(tmp_path))
    writer._rollover_file_size = 10  # For testing purposes
    payload = [{"column1": i, "column2": "data"} for i in range(100)]
    writer.add_payload(payload)
    writer.add_payload(payload)

    # Inspect the created files
    created_files = list(tmp_path.iterdir())
    assert len(created_files) == 2
