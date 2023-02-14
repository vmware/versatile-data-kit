# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from abc import abstractmethod


class ITroubleshootUtility:
    """
    Allows for troubleshoot utilities to be implemented. It provides a unified
    API to be used by all utilities.

    A troubleshooting utility is a utility class, containing logic which is to
    be used for troubleshooting of deployed data jobs.
    """

    @abstractmethod
    def start(self):
        """
        Starts the execution of the utility when the job is initialized.
        The method is called at the `initialize_job` step of the Job lifecycle,
        https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins#data-job-run-execution-cycle

        NOTE: Any troubleshooting utility needs to be self-contained and when
        used should not interfere with the normal operation of the data job.
        The framework will ignore any exception coming from the troubleshooting
        utility and will only log the error message.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Terminates the troubleshooting utility at the end of the data job
        execution. This method should implement everything needed to clean up
        after the utility is used.

        The method is called at the `finalize_job` step of the Job lifecycle,
        https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins#data-job-run-execution-cycle

        NOTE: The framework will ignore any exception coming from the
        troubleshooting utility and will only log the error message.
        """
        pass
