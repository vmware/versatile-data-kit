# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

log = logging.getLogger(__name__)


class WriteToFileAction:
    """
    Writes a string message to a specified file upon completion of a data job execution.

    This is intended to provide a termination status of a data job in a Kubernetes environment
    (see https://kubernetes.io/docs/tasks/debug-application-cluster/determine-reason-pod-failure/).
    Keep in mind that there is a limit to the length of the termination message.
    """

    def __init__(self, filename, show_log_messages=True):
        self.filename = filename
        self.show_log_messages = show_log_messages

    def append_to_file(self, message):
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
