# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput

__author__ = "VMware, Inc."
__copyright__ = (
    "Copyright 2019 VMware, Inc.  All rights reserved. -- VMware Confidential"
)


def run(job_input: IJobInput) -> None:
    template_args = job_input.get_arguments()
    check = template_args.get("check")
    if check:
        check = setup_testing_check(check)
        template_args["check"] = check

    job_input.execute_template(
        template_name="insert", template_args=template_args, database="trino"
    )


def setup_testing_check(check):
    if check == "use_positive_check":
        check = _sample_check_true
    elif check == "use_negative_check":
        check = _sample_check_false
    return check


def _sample_check_true(tmp_table_name):
    return True


def _sample_check_false(tmp_table_name):
    return False
