# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.impala.templates.load.validators import versioned_definition

__author__ = "VMware, Inc."
__copyright__ = (
    "Copyright 2019 VMware, Inc.  All rights reserved. -- VMware Confidential"
)


def run(job_input: IJobInput) -> None:
    args = versioned_definition.validate_arguments(job_input)
    job_input.execute_template(
        template_name="load/versioned",
        template_args=args,
    )
