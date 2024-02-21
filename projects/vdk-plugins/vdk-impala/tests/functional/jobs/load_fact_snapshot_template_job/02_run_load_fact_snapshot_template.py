# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from functional import test_utility
from vdk.api.job_input import IJobInput

__author__ = "VMware, Inc."
__copyright__ = (
    "Copyright 2019 VMware, Inc.  All rights reserved. -- VMware Confidential"
)


def run(job_input: IJobInput) -> None:
    template_args = job_input.get_arguments()
    check = template_args.get("check")
    if check:
        check = test_utility.setup_testing_check(check)
        template_args["check"] = check

    job_input.execute_template(
        template_name="load/fact/snapshot",
        template_args=template_args,
    )
