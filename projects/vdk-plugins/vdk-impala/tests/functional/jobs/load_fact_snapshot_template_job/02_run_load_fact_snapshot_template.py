# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput

__author__ = "VMware, Inc."
__copyright__ = (
    "Copyright 2019 VMware, Inc.  All rights reserved. -- VMware Confidential"
)


def run(job_input: IJobInput) -> None:
    def sample_check_true(tmp_table_name):
        return True

    def sample_check_false(tmp_table_name):
        return False

    template_args = job_input.get_arguments()
    check = template_args.get("check")

    if check == "use_positive_check":
        template_args["check"] = sample_check_true
    elif check == "use_negative_check":
        template_args["check"] = sample_check_false
    job_input.execute_template(
        template_name="load/fact/snapshot",
        template_args=job_input.get_arguments(),
    )
