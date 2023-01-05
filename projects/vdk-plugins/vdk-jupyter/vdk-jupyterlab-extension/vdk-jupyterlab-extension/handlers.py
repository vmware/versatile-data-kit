# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from .vdk import VdkUI


class RunJobHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({"path": f"{os.getcwd()}"}))

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        status_code = VdkUI.run_job(input_data["jobPath"], input_data["jobArguments"])
        self.finish(json.dumps({"message": f"{status_code}"}))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    run_job_route_pattern = url_path_join(base_url, "vdk-jupyterlab-extension", "run")
    run_job_handlers = [(run_job_route_pattern, RunJobHandler)]
    web_app.add_handlers(host_pattern, run_job_handlers)
