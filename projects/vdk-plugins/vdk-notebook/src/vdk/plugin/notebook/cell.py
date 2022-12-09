# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0


class Cell:
    """
    Helper class that retrieves data from Jupyter cells
    Only the data essential for running a VDK data job is saved
    Other data is ignored
    """

    def __init__(self, jupyter_cell):
        self.tags = jupyter_cell["metadata"].get("tags", {})
        self.source = "".join(jupyter_cell["source"])

    def is_vdk_cell(self):
        return "vdk" in self.tags

    def is_sql_cell(self):
        return self.source.startswith("%sql")

    def is_vdk_run_cell(self):
        return "def run(" in self.source

    def add_code(self, cells):
        code = []
        for cell in cells:
            code.append(cell.source)
        self.source = "\n".join(code) + "\n" + self.source

    def get_code(self):
        if self.source.startswith("%sql"):
            code = self.source.replace("%sql", "")
            return code.replace(";", "")
        return self.source
