# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass


@dataclass
class Cell:
    """
    A class that represents Jupyter code cell
    """

    def __init__(self, jupyter_cell):
        self.tags = jupyter_cell["metadata"].get("tags", {})
        self.source = "".join(jupyter_cell["source"])


# TODO: add a better parsing methods
class CellUtils:
    @staticmethod
    def is_vdk_cell(cell: Cell):
        return "vdk" in cell.tags

    @staticmethod
    def is_sql_cell(cell: Cell):
        return cell.source.startswith("%sql")

    @staticmethod
    def get_cell_code(cell: Cell):
        if cell.source.startswith("%sql"):
            code = cell.source.replace("%sql", "")
            return code
        return cell.source
