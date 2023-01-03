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
    def is_vdk_run_cell(cell: Cell):
        return "def run(" in cell.source

    @staticmethod
    def combine_cells(main_cell: Cell, additional_cells):
        code = []
        for cell in additional_cells:
            code.append(cell.source)
        main_cell.source = "\n".join(code) + "\n" + main_cell.source

    @staticmethod
    def get_cell_code(cell: Cell):
        if cell.source.startswith("%sql"):
            code = cell.source.replace("%sql", "")
            return code.replace(";", "")
        return cell.source
