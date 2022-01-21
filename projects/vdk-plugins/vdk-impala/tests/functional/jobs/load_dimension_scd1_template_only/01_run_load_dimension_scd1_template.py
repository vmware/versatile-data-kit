# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.impala.templates.load.validators import dimension_scd1_definition

__author__ = "VMware, Inc."
__copyright__ = (
    "Copyright 2019 VMware, Inc.  All rights reserved. -- VMware Confidential"
)


def run(job_input: IJobInput) -> None:
    args = dimension_scd1_definition.get_validated_arguments(job_input)
    job_input.execute_template(
        template_name="load/dimension/scd1",
        template_args=args,
    )
