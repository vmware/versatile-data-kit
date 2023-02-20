# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput) -> None:
    result = job_input.execute_template(
        template_name="scd2",
        template_args=job_input.get_arguments(),
    )
    if result.is_failed() and result.get_exception():
        raise result.get_exception()
