# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from abc import ABC
from abc import abstractmethod

log = logging.getLogger(__name__)


class ITerminationAction(ABC):
    """
    A base class representing an action that is performed upon data job completion, depending on the result.
    """

    @abstractmethod
    def success(self):
        """
        Called when the job execution was successful.
        """
        pass

    @abstractmethod
    def user_error(self):
        """
        Called when the job execution failed with an user error.
        """
        pass

    @abstractmethod
    def platform_error(self):
        """
        Called when the job execution failed with a platform error.
        """
        pass


class WriteToFileAction(ITerminationAction):
    """
    Writes a string message to a specified file upon completion of a data job execution.

    This is intended to provide a termination status of a data job in a Kubernetes environment
    (see https://kubernetes.io/docs/tasks/debug-application-cluster/determine-reason-pod-failure/).
    Keep in mind that there is a limit to the length of the termination message.
    """

    def __init__(self, filename, show_log_messages=True):
        self.filename = filename
        self.show_log_messages = show_log_messages

    def _append_to_file(self, message):
        if not self.filename:
            return

        try:
            with open(self.filename, "a") as file:
                file.write(message)
        except OSError as e:
            if self.show_log_messages:
                log.debug(
                    f'Unable to write termination message to file "{self.filename}". {e}'
                )

    def success(self):
        self._append_to_file("Success\n")

    def user_error(self):
        self._append_to_file("User error\n")

    def platform_error(self):
        self._append_to_file("Platform error\n")

    def skipped(self):
        self._append_to_file("Skipped\n")
