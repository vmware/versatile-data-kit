# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.trino.trino_utils import TrinoTemplateQueries


def run(job_input: IJobInput) -> None:
    """
    Execute move_data_to_table - the function this job is created to test
    """
    args = job_input.get_arguments()
    db = args.get("db")
    src = args.get("src")
    target = args.get("target")

    trino_queries = TrinoTemplateQueries(job_input)
    trino_queries.move_data_to_table(db, src, db, target)
