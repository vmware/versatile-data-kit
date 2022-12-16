# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess


class VDK:
    """
    A single parent class containing all the individual VDK methods in it.
    """

    @staticmethod
    def run_job(path, arguments=None):
        """
        Execute `run job`.
        When no auth is provided, disables prompts for the password to avoid the terminal hanging.
        When auth is provided, await prompts for username/passwords and sends them
        :param path: the directory where the job run will be performed
        :param arguments: the additional variables for the job run
        :return: response with status code.
        """
        if not os.path.exists(path):
            path = os.getcwd() + path
            if not os.path.exists(path):
                return "Incorrect path!"
        p = (
            subprocess.run(
                f"vdk run {path} 2> vdk_logs.txt",
                shell=True,
                check=True,
                capture_output=True,
            )
            if not arguments
            else subprocess.run(
                f"vdk run {path} --arguments {arguments} 2> vdk_logs.txt",
                shell=True,
                check=True,
                capture_output=True,
            )
        )
        return p.returncode
