# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput

__author__ = "VMware, Inc."
__copyright__ = (
    "Copyright 2019 VMware, Inc.  All rights reserved. -- VMware Confidential"
)


def run(job_input: IJobInput) -> None:
    job_input.execute_template(
        template_name="load/dimension/scd1",
        template_args=job_input.get_arguments(),
    )
