# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass

from vdk.internal.builtin_plugins.run.file_based_step import TYPE_PYTHON
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_SQL


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
        self.id = jupyter_cell["id"]

    @staticmethod
    def __extract_source_code(jupyter_cell):
        lines = jupyter_cell["source"]
        if lines and lines[0].strip().startswith("%%vdksql"):
            statement = "".join(lines[1:])
            return statement, TYPE_SQL
        return "".join(lines), TYPE_PYTHON
