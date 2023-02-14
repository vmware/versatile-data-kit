# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    args = job_input.get_arguments()

    sql = f"""
        insert into {args['target_table']}
        select * from {args['source_table']}
    """
    job_input.execute_query(sql)
