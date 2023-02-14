# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    rows = [[i, i + 1, "hi"] for i in range(100)]
    job_input.send_tabular_data_for_ingestion(
        rows, column_names=["index", "next", "word"], destination_table="test"
    )
