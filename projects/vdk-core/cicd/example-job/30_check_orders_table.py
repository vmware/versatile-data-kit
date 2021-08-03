# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Detailed documentation of VDK provided functionalities in job_input object can be found here in the user wiki
"""
import logging


def run(job_input):
    """
    This method is called automatically during execution. Only scripts containing this method are executed by VDK.
       Arguments:
          job_input: object automatically passed to run() method by VDK on execution.
    """
    result = job_input.execute_query(
        """
      select count(1) from orders
   """
    )
    if result and result[0][0] > 0:
        logging.getLogger(__name__).info("Job has completed successfully")
    else:
        raise Exception("Job has failed. Could not get correct number of rows.")
