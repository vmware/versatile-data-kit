# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.api.job_input import IJobInput


def run(job_input: IJobInput):

    counter = job_input.get_arguments().get("counter")
    job_input.execute_query(f"insert into test_table VALUES ('one', {counter})")
