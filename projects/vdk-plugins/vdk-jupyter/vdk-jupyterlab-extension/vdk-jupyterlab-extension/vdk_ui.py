# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import shlex
import subprocess

from vdk.internal.control.command_groups.job.create import JobCreate
from vdk.internal.control.command_groups.job.delete import JobDelete
from vdk.internal.control.command_groups.job.download_job import JobDownloadSource
from vdk.internal.control.utils import cli_utils

from .dict_object import DictObj


class VdkUI:
    """
    A single parent class containing all the individual VDK methods in it.
    """

    @staticmethod
    def run_job(job_data: DictObj):
        """
        Execute `run job`.
        :param job_data: the job data
        following the projects/vdk-plugins/vdk-jupyter/vdk-jupyterlab-extension/src/dataClasses/jobDataModel.json
        :return: response with status code.
        """
        if not os.path.exists(job_data.jobPath):
            job_data.jobPath = os.getcwd() + job_data.jobPath
            if not os.path.exists(job_data.jobPath):
                return "Incorrect path!"
        with open("vdk_logs.txt", "w+") as log_file:
            path = shlex.quote(job_data.jobPath)
            cmd: list[str] = ["vdk", "run", f"{path}"]
            if job_data.jobArguments:
                arguments = shlex.quote(job_data.jobArguments)
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
    def delete_job(job_data: DictObj):
        """
        Execute `delete job`.
        :param job_data: the job data
        following the projects/vdk-plugins/vdk-jupyter/vdk-jupyterlab-extension/src/dataClasses/jobDataModel.json
        :return: message that the job is deleted
        """
        cmd = JobDelete(job_data.restApiUrl)
        cmd.delete_job(job_data.jobName, job_data.jobTeam)
        return f"Deleted the job with name {job_data.jobName} from {job_data.jobTeam} team. "

    @staticmethod
    def download_job(job_data: DictObj):
        """
        Execute `download job`.
        :param job_data: the job data
        following the projects/vdk-plugins/vdk-jupyter/vdk-jupyterlab-extension/src/dataClasses/jobDataModel.json
        :return: message that the job is downloaded
        """
        cmd = JobDownloadSource(job_data.restApiUrl)
        if not os.path.exists(job_data.jobPath):
            job_data.jobPath = os.getcwd() + job_data.jobPath
            if not os.path.exists(job_data.jobPath):
                return "Incorrect path!"
        cmd.download(job_data.jobTeam, job_data.jobName, job_data.jobPath)
        return f"Downloaded the job with name {job_data.jobName} to {job_data.jobTeam}. "

    # TODO: make it work with notebook jobs
    @staticmethod
    def create_job(job_data: DictObj):
        """
        Execute `create job`.
        :param job_data: the job data
        following the projects/vdk-plugins/vdk-jupyter/vdk-jupyterlab-extension/src/dataClasses/jobDataModel.json
        :return: message that the job is created
        """
        local = True if job_data.local else False
        cloud = True if job_data.cloud else False
        cmd = JobCreate(job_data.restApiUrl)
        if cloud:
            cli_utils.check_rest_api_url(job_data.restApiUrl)

        if local:
            if not os.path.exists(job_data.jobPath):
                job_data.jobPath = os.getcwd() + job_data.jobPath
                if not os.path.exists(job_data.jobPath):
                    return "Incorrect path!"
            cmd.validate_job_path(job_data.jobPath, job_data.jobName)

        cmd.create_job(job_data.jobName, job_data.jobTeam,  job_data.jobPath, cloud, local)
        return f"Job with name {job_data.jobName} was created."
