# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Detailed documentation of VDK provided functionalities in job_input object can be found in the user wiki
"""
import logging

log = logging.getLogger(__name__)


def run(job_input):
    """
    This method is called automatically during execution. Only scripts containing this method are executed by VDK.
       Arguments:
          job_input: object automatically passed to run() method by VDK on execution.
    """
    log.debug(f"Start data job step {__name__}.")
    result = job_input.execute_query(
        """
      select count(1) from orders
   """
    )
    if result and result[0][0] > 0:
        log.info("Job has completed successfully")
    else:
        raise Exception("Job has failed. Could not get correct number of rows.")
