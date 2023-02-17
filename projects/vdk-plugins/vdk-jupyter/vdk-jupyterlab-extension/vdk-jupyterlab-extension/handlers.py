# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from .vdk_ui import VdkUI
from .dict_object import DictObj


class RunJobHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({"path": f"{os.getcwd()}"}))

    @tornado.web.authenticated
    def post(self):
        job_data = DictObj(self.get_json_body())
        status_code = VdkUI.run_job(job_data.jobPath, job_data.jobArguments)
        self.finish(json.dumps({"message": f"{status_code}"}))


class DeleteJobHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        job_data = DictObj(self.get_json_body())
        try:
            status = VdkUI.delete_job(
                job_data.jobName, job_data.jobTeam, job_data.restApiUrl
            )
            self.finish(json.dumps({"message": f"{status}", "error": ""}))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class DownloadJobHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        job_data = DictObj(self.get_json_body())
        try:
            status = VdkUI.download_job(
                job_data.jobName,
                job_data.jobTeam,
                job_data.restApiUrl,
                job_data.jobPath,
            )
            self.finish(json.dumps({"message": f"{status}", "error": ""}))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


class CreateJobHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        job_data = DictObj(self.get_json_body())
        try:
            local = True if job_data.local else False
            cloud = True if job_data.cloud else False
            status = VdkUI.create_job(
                job_data.jobName,
                job_data.jobTeam,
                job_data.restApiUrl,
                job_data.jobPath,
                local,
                cloud,
            )
            self.finish(json.dumps({"message": f"{status}", "error": ""}))
        except Exception as e:
            self.finish(json.dumps({"message": f"{e}", "error": "true"}))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    run_job_route_pattern = url_path_join(base_url, "vdk-jupyterlab-extension", "run")
    run_job_handlers = [(run_job_route_pattern, RunJobHandler)]
    web_app.add_handlers(host_pattern, run_job_handlers)

    delete_job_route_pattern = url_path_join(
        base_url, "vdk-jupyterlab-extension", "delete"
    )
    delete_job_handlers = [(delete_job_route_pattern, DeleteJobHandler)]
    web_app.add_handlers(host_pattern, delete_job_handlers)

    download_job_route_pattern = url_path_join(
        base_url, "vdk-jupyterlab-extension", "download"
    )
    download_job_handlers = [(download_job_route_pattern, DownloadJobHandler)]
    web_app.add_handlers(host_pattern, download_job_handlers)

    create_job_route_pattern = url_path_join(
        base_url, "vdk-jupyterlab-extension", "create"
    )
    create_job_handlers = [(create_job_route_pattern, CreateJobHandler)]
    web_app.add_handlers(host_pattern, create_job_handlers)
