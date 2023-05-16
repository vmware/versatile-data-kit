# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
import shlex
import subprocess
from pathlib import Path

from vdk.internal.control.command_groups.job.create import JobCreate
from vdk.internal.control.command_groups.job.delete import JobDelete
from vdk.internal.control.command_groups.job.deploy_cli_impl import JobDeploy
from vdk.internal.control.command_groups.job.download_job import JobDownloadSource
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils.cli_utils import get_or_prompt


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
                return {"message": f"Incorrect path! {path} does not exist!"}
        script_files = [
            x
            for x in Path(path).iterdir()
            if (
                x.name.lower().endswith(".ipynb")
                or x.name.lower().endswith(".py")
                or x.name.lower().endswith(".sql")
            )
        ]
        if len(script_files) == 0:
            return {"message": f"No steps were found in {path}!"}
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
            if process.returncode != 0:
                job_name = (
                    os.path.basename(path[:-1])
                    if path.endswith("/")
                    else os.path.basename(path)
                )
                error_file = os.path.join(
                    os.path.dirname(path), f".{job_name}_error.json"
                )
                if os.path.exists(error_file):
                    with open(error_file) as file:
                        # the json is generated in vdk-notebook plugin
                        # you can see /vdk-notebook/src/vdk/notebook-plugin.py
                        error = json.load(file)
                        return {"message": error["details"]}
            return {"message": process.returncode}

    @staticmethod
    def delete_job(name: str, team: str, rest_api_url: str):
        """
        Execute `delete job`.
        :param name: the name of the data job that will be deleted
        :param team: the team of the data job that will be deleted
        :param rest_api_url: The base REST API URL.
        :return: message that the job is deleted
        """
        cmd = JobDelete(rest_api_url)
        cmd.delete_job(name, team)
        return f"Deleted the job with name {name} from {team} team. "

    @staticmethod
    def download_job(name: str, team: str, rest_api_url: str, path: str):
        """
        Execute `download job`.
        :param name: the name of the data job that will be downloaded
        :param team: the team of the data job that will be downloaded
        :param rest_api_url: The base REST API URL
        :param path: the path to the directory where the job will be downloaded
        :return: message that the job is downloaded
        """
        cmd = JobDownloadSource(rest_api_url)
        cmd.download(team, name, path)
        return f"Downloaded the job with name {name} to {path}. "

    # TODO: make it work with notebook jobs
    @staticmethod
    def create_job(
        name: str, team: str, rest_api_url: str, path: str, local: bool, cloud: bool
    ):
        """
        Execute `create job`.
        :param name: the name of the data job that will be created
        :param team: the team of the data job that will be created
        :param rest_api_url: The base REST API URL
        :param path: the path to the directory where the job will be created
        :param local: create sample job on local file system
        :param cloud: create job in the cloud
        :return: message that the job is created
        """
        cmd = JobCreate(rest_api_url)
        if cloud:
            cli_utils.check_rest_api_url(rest_api_url)

        if local:
            cmd.validate_job_path(path, name)

        cmd.create_job(name, team, path, cloud, local)
        return f"Job with name {name} was created."

    @staticmethod
    def create_deployment(
        name: str, team: str, rest_api_url: str, path: str, reason: str, enabled: bool
    ):
        """
        Execute `Deploy job`.
        :param name: the name of the data job that will be deployed
        :param team: the team of the data job that will be depployed
        :param rest_api_url: The base REST API URL
        :param path: the path to the job's directory
        :param reason: the reason of deployment
        :param enabled: flag whether the job is enabled (that will basically un-pause the job)
        :return: output string of the operation
        """
        output = ""
        cmd = JobDeploy(rest_api_url, output)
        path = get_or_prompt("Job Path", path)
        default_name = os.path.basename(path)
        name = get_or_prompt("Job Name", name, default_name)
        reason = get_or_prompt("Reason", reason)
        cmd.create(
            name=name,
            team=team,
            job_path=path,
            reason=reason,
            output=output,
            vdk_version=None,
            enabled=enabled,
        )
        return output

    @staticmethod
    def get_notebook_info(cell_id: str, pr_path: str):
        """
        Return information about the notebook that includes a cell with a given id
        :param cell_id: the id of the cell
        :param pr_path: the path to the parent directory of the notebook
        :return: path of the notebook, index of the cell
             if the specified parent directory does not exist, an empty dictionary is returned.
        """
        if not os.path.exists(pr_path):
            pr_path = os.getcwd() + pr_path
            if not os.path.exists(pr_path):
                return {"path": "", "cellIndex": ""}
        notebook_files = [
            x
            for x in pathlib.Path(pr_path).iterdir()
            if (x.name.lower().endswith(".ipynb"))
        ]
        for notebook_file in notebook_files:
            with open(notebook_file) as f:
                notebook_json = json.load(f)
                cell_index = 0
                for jupyter_cell in notebook_json["cells"]:
                    if jupyter_cell["id"] == cell_id:
                        notebook_path = str(notebook_file).replace(os.getcwd(), "")
                        return {
                            "path": str(notebook_path),
                            "cellIndex": str(cell_index),
                        }
                    cell_index += 1
        return {"path": "", "cellIndex": ""}

    @staticmethod
    def get_vdk_tagged_cell_indices(notebook_path: str):
        """
        Return the indices of the notebook cells that are tagged with 'vdk'
        :param notebook_path: Path to the notebook file.
        :return: A list containing the indices of the cells tagged with 'vdk'.
             If the specified notebook path does not exist, an empty list is returned.
        """
        if not os.path.exists(notebook_path):
            job_notebook = os.getcwd() + notebook_path
            if not os.path.exists(job_notebook):
                return []
        with open(notebook_path) as f:
            notebook_json = json.load(f)
            vdk_cells = []
            cell_index = 0
            for jupyter_cell in notebook_json["cells"]:
                if "vdk" in jupyter_cell["metadata"].get("tags", {}):
                    vdk_cells.append(cell_index)
                cell_index += 1
            return vdk_cells
