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
