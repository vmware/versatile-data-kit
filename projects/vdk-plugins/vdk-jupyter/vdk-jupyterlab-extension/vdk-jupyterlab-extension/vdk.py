# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import shlex
import subprocess


class VdkUI:
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
        with open("vdk_logs.txt", "w+") as log_file:
            path = shlex.quote(path)
            arguments = shlex.quote(arguments)
            cmd_str = (
                f"vdk run {path}"
                if not arguments
                else f"vdk run {path} --arguments {arguments}"
            )
            cmd = shlex.split(cmd_str)
            process = subprocess.Popen(
                cmd, stdout=log_file, stderr=log_file, env=os.environ.copy()
            )
            subprocess.check_output(["/bin/ls", "-l"])
            process.wait()
            return f"{process.returncode}"
