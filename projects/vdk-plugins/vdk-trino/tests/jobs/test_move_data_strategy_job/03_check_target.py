# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput) -> None:
    """
    Check whether move data step successfully wrote data to target
    """
    args = job_input.get_arguments()
    db = args.get("db")
    target = args.get("target")

    result = job_input.execute_query(
        f"""
        SELECT COUNT (1) from {db}.{target}
        """
    )
    if result and result[0][0] > 0:
        logging.getLogger(__name__).info("Job has completed successfully.")
    else:
        raise Exception("Job has failed. Could not get correct number of rows.")
