# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass

from vdk.internal.builtin_plugins.run.file_based_step import TYPE_PYTHON
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_SQL
from vdk.plugin.notebook.vdk_ingest import TYPE_INGEST


@dataclass
class Cell:
    """
    A class that represents Jupyter code cell
    See Jupyter cell in this json schema:
             https://github.com/jupyter/nbformat/blob/main/nbformat/v4/nbformat.v4.schema.json
    """

    def __init__(self, jupyter_cell):
        self.tags = jupyter_cell["metadata"].get("tags", {})
        self.source, self.source_type = self.__extract_source_code(jupyter_cell)
        self.id = jupyter_cell.get("id")

    @staticmethod
    def __extract_source_code(jupyter_cell):
        lines = jupyter_cell["source"]
        if lines and lines[0].strip().startswith("%%vdksql"):
            statement = "".join(lines[1:])
            return statement, TYPE_SQL
        if lines and lines[0].strip().startswith("%%vdkingest"):
            source = "".join(lines[1:])
            return source, TYPE_INGEST
        return "".join(lines), TYPE_PYTHON
