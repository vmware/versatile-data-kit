# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


class BrokenIterator:
    """Class to implement an iterator
    of powers of two"""

    def __init__(self, break_at_index=3):
        self._break_at_index = break_at_index

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n <= self._break_at_index:
            self.n += 1
            return [1, 2]
        else:
            raise FloatingPointError("foo")


def run(job_input: IJobInput):
    ingest_some_data(job_input)


def ingest_some_data(job_input):
    job_input.send_tabular_data_for_ingestion(
        rows=BrokenIterator(), column_names=["a", "b"]
    )
