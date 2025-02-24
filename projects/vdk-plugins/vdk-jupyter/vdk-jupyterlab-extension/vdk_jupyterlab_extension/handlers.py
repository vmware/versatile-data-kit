# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from . import VdkJupyterConfig
from .job_data import JobDataLoader
from .oauth2 import OAuth2Handler
from .task_runner import TaskRunner
from .vdk_options.vdk_options import VdkOption
from .vdk_ui import VdkUI

log = logging.getLogger(__name__)
task_runner = TaskRunner()


def task_start_response_success(task_id):
    """Helper function to generate a JSON response for a successful task start request.

    :param task_id: The task ID.
    :return: A JSON response.
    """
    return json.dumps({"message": f"Task {task_id} started", "error": ""})


def task_start_response_failure(task_type):
    """Helper function to generate a JSON response for a failing task start request.

    :param task_type: The type of the task being started.
    :return: A JSON response.
    """
    return json.dumps(
        {
            "message": f"Task {task_type} failed to start",
            "error": "Another task is already running",
        }
    )


class GetTaskStatusHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        task_id = self.get_argument("taskId", default=None)

        if not task_id:
            self.set_status(400)
            self.finish(json.dumps({"error": "taskId not provided."}))
            return
        try:
            current_status = task_runner.get_status()
            if current_status["task_id"] != task_id:
                self.finish(
                    json.dumps(
                        {
                            "status": "failed",
                            "message": "Mismatched taskId.",
                            "error": f"Requested status for {task_id} but currently processing {current_status['task_id']}",
                        }
                    )
                )
                return

            self.finish(json.dumps(current_status))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class LoadJobDataHandler(APIHandler):
    """
    Class responsible for handling POST request for retrieving data(full path, job's name and team)
     about job of directory
     Response: return a json formatted str providing the data about the job
    """

    @tornado.web.authenticated
    def post(self):
        working_directory = json.loads(self.get_json_body())[VdkOption.PATH.value]
        try:
            data = JobDataLoader(working_directory)
            self.finish(
                json.dumps(
                    {
                        VdkOption.PATH.value: data.get_job_jupyter_path(),
                        VdkOption.NAME.value: data.get_job_name(),
                        VdkOption.TEAM.value: data.get_team_name(),
                    }
                )
            )
        except Exception as e:
            log.debug(
                f"Failed to load job information from config.ini with error: {e}."
            )
            self.finish(
                json.dumps(
                    {
                        VdkOption.PATH.value: "",
                        VdkOption.NAME.value: "",
                        VdkOption.TEAM.value: "",
                    }
                )
            )


class RunJobHandler(APIHandler):
    """
    Class responsible for handling POST request for running a Data Job given its path and arguments to run with
    Response: return a json formatted str including:
     ::error field with error message if an error exists
     ::message field with status of the VDK operation
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        try:
            task_id = task_runner.start_task(
                "RUN",
                lambda: VdkUI.run_job(
                    input_data[VdkOption.PATH.value],
                    input_data[VdkOption.ARGUMENTS.value],
                ),
            )

            if task_id:
                self.finish(task_start_response_success(task_id))
            else:
                self.finish(task_start_response_failure("RUN"))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class DownloadJobHandler(APIHandler):
    """
    Class responsible for handling POST request for downloading a Data Job given its name, team,
    Rest API URL, and the path to where the job will be downloaded
    Response: return a json formatted str including:
        ::error field with error message if an error exists
        ::message field with status of the Vdk operation
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        try:
            task_id = task_runner.start_task(
                "DOWNLOAD",
                lambda: VdkUI.download_job(
                    input_data[VdkOption.NAME.value],
                    input_data[VdkOption.TEAM.value],
                    input_data[VdkOption.PATH.value],
                ),
            )

            if task_id:
                self.finish(task_start_response_success(task_id))
            else:
                self.finish(task_start_response_failure("DOWNLOAD"))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class ConvertJobHandler(APIHandler):
    """
    Class responsible for handling POST request for transforming a directory type Data job(with .py and .sql files)
    to a notebook type data job
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        try:
            task_id = task_runner.start_task(
                "CONVERTJOBTONOTEBOOK",
                lambda: VdkUI.convert_job(input_data[VdkOption.PATH.value]),
            )

            if task_id:
                self.finish(task_start_response_success(task_id))
            else:
                self.finish(task_start_response_failure("CONVERTJOBTONOTEBOOK"))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class CreateJobHandler(APIHandler):
    """
    Class responsible for handling POST request for creating a Data Job given its name, team,
    flags whether it will be created locally or in the cloud, path to where job will be created (if local),
    Rest API URL (if cloud)
    Response: return a json formatted str including:
        ::error field with error message if an error exists
        ::message field with status of the Vdk operation
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        try:
            task_id = task_runner.start_task(
                "CREATE",
                lambda: VdkUI.create_job(
                    input_data[VdkOption.NAME.value],
                    input_data[VdkOption.TEAM.value],
                    input_data[VdkOption.PATH.value],
                ),
            )

            if task_id:
                self.finish(task_start_response_success(task_id))
            else:
                self.finish(task_start_response_failure("CREATE"))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class CreateDeploymentHandler(APIHandler):
    """
    Class responsible for handling POST request for creating a deployment of  Data Job given its name, team, path,
    Rest API URL, deployment reason and flag whether it is enabled (that will basically un-pause the job)
    Response: return a json formatted str including:
        ::error field with error message if an error exists
        ::message field with status of the Vdk operation
    """

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        try:
            task_id = task_runner.start_task(
                "DEPLOY",
                lambda: VdkUI.create_deployment(
                    input_data[VdkOption.NAME.value],
                    input_data[VdkOption.TEAM.value],
                    input_data[VdkOption.PATH.value],
                    input_data[VdkOption.DEPLOYMENT_REASON.value],
                ),
            )

            if task_id:
                self.finish(task_start_response_success(task_id))
            else:
                self.finish(task_start_response_failure("DEPLOY"))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class GetNotebookInfoHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        notebook_info = VdkUI.get_notebook_info(
            input_data["cellId"], input_data[VdkOption.PATH.value]
        )
        self.finish(json.dumps(notebook_info))


class GetVdkCellIndicesHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        vdk_indices = VdkUI.get_vdk_tagged_cell_indices(input_data["nbPath"])
        self.finish(json.dumps(vdk_indices))


class GetServerPathHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps(os.getcwd()))


def setup_handlers(web_app, vdk_config: VdkJupyterConfig):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    def add_handler(handler, endpoint, args=None):
        job_route_pattern = url_path_join(
            base_url, "vdk-jupyterlab-extension", endpoint
        )
        if args is None:
            args = {}
        job_handlers = [(job_route_pattern, handler, args)]
        log.info(f"Job handlers: {job_handlers}")
        web_app.add_handlers(host_pattern, job_handlers)

    add_handler(OAuth2Handler, "login", {"vdk_config": vdk_config})
    add_handler(GetTaskStatusHandler, "taskStatus")
    add_handler(RunJobHandler, "run")
    add_handler(DownloadJobHandler, "download")
    add_handler(ConvertJobHandler, "convertJobToNotebook")
    add_handler(CreateJobHandler, "create")
    add_handler(LoadJobDataHandler, "job")
    add_handler(CreateDeploymentHandler, "deploy")
    add_handler(GetNotebookInfoHandler, "notebook")
    add_handler(GetVdkCellIndicesHandler, "vdkCellIndices")
    add_handler(GetServerPathHandler, "serverPath")
