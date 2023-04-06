# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass


@dataclass
class Cell:
    """
    A class that represents Jupyter code cell
    See Jupyter cell in this json schema:
             https://github.com/jupyter/nbformat/blob/main/nbformat/v4/nbformat.v4.schema.json
    """

    def __init__(self, jupyter_cell):
        self.tags = jupyter_cell["metadata"].get("tags", {})
        self.source = "".join(jupyter_cell["source"])
        self.id = jupyter_cell["id"]
