# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import shlex
import subprocess

from vdk.internal.control.command_groups.job.delete import JobDelete


class VdkUI:
    """
    A single parent class containing all the individual VDK methods in it.
    """

    @staticmethod
    def run_job(path, arguments=None):
        """
        Execute `run job`.
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
            cmd: list[str] = ["vdk", "run", f"{path}"]
            if arguments:
                arguments = shlex.quote(arguments)
                cmd.append("--arguments")
                cmd.append(f"{arguments}")
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=log_file,
                env=os.environ.copy(),
                shell=False,
            )
            process.wait()
            return f"{process.returncode}"

    @staticmethod
    def delete_job(name: str, team: str, rest_api_url: str):
        """
        Execute `delete job`.
        :param name: the name of the data job that will be deleted
        :param team: the team of the data job that will be deleted
        :param rest_api_url: The base REST API URL.
        :return: message that the job is deleted
        """
        try:
            cmd = JobDelete(rest_api_url)
            cmd.delete_job(name, team)
            return f"Deleted the job with name {name} from {team} team. "
        except Exception as e:
            raise e
