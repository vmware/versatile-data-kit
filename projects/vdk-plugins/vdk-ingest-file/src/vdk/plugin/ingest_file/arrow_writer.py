# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import atexit
import os
from threading import RLock
from typing import Dict
from typing import List
from typing import Optional

import pandas
import pyarrow
from vdk.plugin.ingest_file import pyarrow_utils


class ArrowWriter:
    def __init__(self, directory_path: str):
        self._rollover_file_size = 128 * 1024 * 1024
        self._filename = None
        self._directory_path = directory_path
        self._index = 0
        self._schema: Optional[pyarrow.Schema] = None
        self._file_handle: Optional[pyarrow.OSFile] = None
        self._file_writer: Optional[pyarrow.RecordBatchFileWriter] = None
        self._lock = RLock()

        atexit.register(self.close)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def add_payload(self, payload: List[Dict]):
        with self._lock:
            self._write_payloads_to_file(payload)

    def close(self):
        with self._lock:
            if self._file_writer:
                self._file_writer.close()
                self._file_writer = None
            if self._file_handle:
                self._file_handle.close()
                self._file_handle = None

    @staticmethod
    def _infer_schema(payload: List[Dict]):
        column_types = pyarrow_utils.infer_column_types(payload)
        return pyarrow_utils.python_types_to_pyarrow_schema(column_types)

    def _initialize_new_file(self):
        self.close()
        self._index += 1
        file_path = self._file_path()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self._file_handle = pyarrow.OSFile(file_path, "wb")
        self._file_writer = pyarrow.RecordBatchFileWriter(
            self._file_handle, self._schema
        )

    def _file_path(self) -> str:
        return os.path.join(self._directory_path, f"{self._index:010}.arrow")

    def _write_payloads_to_file(self, payload: List[Dict]):
        if not self._schema:
            self._schema = self._infer_schema(payload)

        df = pandas.DataFrame(payload)
        new_table = pyarrow.table(df)

        if not self._file_writer:
            self._initialize_new_file()

        if new_table.schema != self._schema:
            self._initialize_new_file()
            self._schema = new_table.schema

        if (
            os.path.exists(self._file_path())
            and os.path.getsize(self._file_path()) > self._rollover_file_size
        ):
            self._initialize_new_file()
        self._file_writer.write_table(new_table)
