# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from vdk.internal.builtin_plugins.run.summary_output import JobSummaryParser
from vdk.internal.control.command_groups.job.create import JobCreate
from vdk.internal.control.command_groups.job.deploy_cli_impl import JobDeploy
from vdk.internal.control.command_groups.job.download_job import JobDownloadSource
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils.output_printer import InMemoryTextPrinter
from vdk_jupyterlab_extension.convert_job import ConvertJobDirectoryProcessor
from vdk_jupyterlab_extension.convert_job import DirectoryArchiver
from vdk_jupyterlab_extension.jupyter_notebook import clear_notebook_outputs


class RestApiUrlConfiguration:
    @staticmethod
    def get_rest_api_url():
        try:
            rest_api_url = os.environ["REST_API_URL"]
        except Exception as e:
            raise ValueError(
                "What happened: Missing environment variable REST_API_URL.\n"
                "Why it happened: This is probably caused by a corrupt environment.\n"
                "Consequences: The current environment cannot work as it cannot connect to the VDK Control Service.\n"
                "Countermeasures: Please alert your support team; alternatively, try restarting your environment."
            )
        return rest_api_url


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
        path = expand_path(path)
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
        with open("vdk_run.log", "w+") as log_file:
            cmd = VdkUI.__prepare_vdk_run_command(arguments, path)
            with tempfile.NamedTemporaryFile(
                prefix="jupyter-run-summary-", mode="w+"
            ) as summary_output_file:
                environ_copy = os.environ.copy()
                environ_copy["JOB_RUN_SUMMARY_FILE_PATH"] = summary_output_file.name
                # We add the PYTHONUNBUFFERED env variable to ensure print statements inside user jobs are correctly
                # interspersed in between the rest of the job logs instead of being placed at the end
                environ_copy["PYTHONUNBUFFERED"] = "x"

                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=log_file,
                        stderr=log_file,
                        env=environ_copy,
                        shell=False,
                    )
                    process.wait()
                    if process.returncode != 0:
                        content = pathlib.Path(summary_output_file.name).read_text()
                        job_summary = JobSummaryParser.from_json(content)
                        return {"message": job_summary.details}
                    else:
                        return {"message": process.returncode}
                except Exception as e:
                    return {"message": f"Unhandled exception: {e}"}

    @staticmethod
    def __prepare_vdk_run_command(arguments, path):
        path = shlex.quote(str(path))
        cmd: list[str] = ["vdk", "run", f"{path}"]
        if arguments:
            arguments = shlex.quote(arguments)
            cmd.append("--arguments")
            cmd.append(f"{arguments}")
        return cmd

    @staticmethod
    def download_job(name: str, team: str, path: str) -> str:
        """
        Execute `download job`.
        :param name: the name of the data job that will be downloaded
        :param team: the team of the data job that will be downloaded
        :param path: the path to the directory where the job will be downloaded
        :return: message that the job is downloaded
        """
        cmd = JobDownloadSource(RestApiUrlConfiguration.get_rest_api_url())
        cmd.download(team, name, expand_path(path))
        return f"Downloaded the job with name {name} to {path}. "

    @staticmethod
    def create_job(name: str, team: str, path: str) -> str:
        """
        Execute `create job`.
        :param name: the name of the data job that will be created
        :param team: the team of the data job that will be created
        :param path: the path to the directory where the job will be created
        :return: message that the job is created
        """
        jupyter_job_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "jupyter_sample_job")
        )
        rest_api_url = ""
        cloud = False
        error = ""
        try:
            rest_api_url = RestApiUrlConfiguration.get_rest_api_url()
            cli_utils.check_rest_api_url(rest_api_url)
            cloud = True
        except ValueError as e:
            error = str(e)
        cmd = JobCreate(rest_api_url)
        cmd.create_job(
            name, team, expand_path(path), cloud, True, pathlib.Path(jupyter_job_dir)
        )
        if cloud:
            result = f"Job with name {name} was created successfully!"
        else:
            result = (
                f"Job with name {name} was created only locally. "
                f"If you are not using the Control Service the next lines should not concern you! \n"
                f"We tried to create it in the cloud but come up to:"
                f"{error}"
                f""
            )

        return result

    @staticmethod
    def create_deployment(name: str, team: str, path: str, reason: str):
        """
        Execute `Deploy job`.
        :param name: the name of the data job that will be deployed
        :param team: the team of the data job that will be deployed
        :param path: the path to the job's directory
        :param reason: the reason of deployment
        :return: output string of the operation
        """
        path = expand_path(path)
        with tempfile.TemporaryDirectory() as temp_dir:
            if not os.path.exists(path):
                raise NotADirectoryError(
                    f"The provided path '{path}' is not a valid directory."
                )

            # Copy the contents of the original directory to the temporary directory
            for item in os.listdir(path):
                source_item = os.path.join(path, item)
                destination_item = os.path.join(temp_dir, item)
                if os.path.isdir(source_item):
                    shutil.copytree(source_item, destination_item)
                else:
                    shutil.copy2(source_item, destination_item)

            # Clear outputs for all notebooks in the temporary directory
            for dir_path, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    if filename.endswith(".ipynb"):
                        notebook_path = os.path.join(dir_path, filename)
                        clear_notebook_outputs(notebook_path)

            printer = InMemoryTextPrinter()

            try:
                cmd = JobDeploy(RestApiUrlConfiguration.get_rest_api_url(), printer)
                cmd.create(
                    name=name,
                    team=team,
                    job_path=temp_dir,
                    reason=reason,
                    vdk_version=None,
                    enabled=True,
                )
                return (
                    f"Request to deploy job with name {name} and team {team} is sent successfully!"
                    f"It would take a few minutes for the Data Job to be deployed in the server."
                    f"If notified_on_job_deploy option in config.ini is configured then "
                    f"notification will be sent on successful deploy or in case of an error.\n\n"
                    f"Deployment information:\n {printer.get_memory().strip()}"
                )

            finally:
                # Temporary directory will be automatically cleaned up
                pass

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
            pr_path = expand_path(pr_path)
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
                for index, jupyter_cell in enumerate(notebook_json["cells"]):
                    if jupyter_cell["id"] == cell_id:
                        notebook_path = str(notebook_file).replace(os.getcwd(), "")
                        return {
                            "path": str(notebook_path),
                            "cellIndex": str(index),
                        }
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
            notebook_path = expand_path(notebook_path)
            if not os.path.exists(notebook_path):
                return []
        with open(notebook_path) as f:
            notebook_json = json.load(f)
            vdk_cells = []
            for index, jupyter_cell in enumerate(notebook_json["cells"]):
                if "vdk" in jupyter_cell["metadata"].get("tags", {}):
                    vdk_cells.append(index)
            return vdk_cells

    @staticmethod
    def convert_job(job_dir: str):
        """
        Transforms the job in the specified directory by archiving it, processing the Python and SQL files,
        and returning a processed code structure.
        :param job_dir: Path to the directory of the job to be transformed.
        :return: The processed code structure.
        """
        job_dir = Path(expand_path(job_dir))
        archiver = DirectoryArchiver(job_dir)
        processor = ConvertJobDirectoryProcessor(job_dir)
        archiver.archive_folder()
        processor.process_files()
        message = {
            "code_structure": processor.get_code_structure(),
            "removed_files": processor.get_removed_files(),
        }
        processor.cleanup()
        return message


def expand_path(path: str):
    """
    Expands the path parameter to be rooted at the file system location where Jupyter was initially ran.

    :param path: path parameter provided by the user
    :return: expanded path
    """
    return pathlib.Path(os.getcwd()).joinpath(path)
