# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.api.job_input import IJobInput


def run(job_input: IJobInput) -> None:
    result = job_input.execute_template(
        template_name="scd1",
        template_args=job_input.get_arguments(),
    )
    if result.is_failed() and result.get_exception():
        raise result.get_exception()
