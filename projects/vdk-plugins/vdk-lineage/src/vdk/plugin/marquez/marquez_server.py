# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import subprocess
import time
import webbrowser
from typing import List

log = logging.getLogger(__name__)


def execute(command, success_codes=(0,), env=None):
    """Run a shell command."""
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        status = 0
    except subprocess.CalledProcessError as error:
        output = error.output or b""
        status = error.returncode
        command = error.cmd

    if status not in success_codes:
        raise Exception(
            'Command {} returned {}: """{}""".'.format(
                command, status, output.decode("utf-8")
            )
        )
    return output


class DockerComposeExecutor:
    _compose_files: List[str]
    _compose_project_name: str

    def __init__(self):
        import vdk.plugin.marquez

        module_path = vdk.plugin.marquez.__path__._path[0]
        dir = os.path.abspath(module_path)

        self._compose_files = [os.path.join(dir, "docker-compose.yaml")]
        self._compose_project_name = "vdk-marquez-server"

    def execute(self, subcommand):
        command = "docker-compose"
        for compose_file in self._compose_files:
            command += f' -f "{compose_file}"'
        command += f' -p "{self._compose_project_name}" {subcommand}'
        return execute(command)

    def up(self):
        self.execute("up --build -d")

    def down(self):
        self.execute("down -v")


class MarquezInstaller:
    def __init__(self):
        self._compose_executor = DockerComposeExecutor()

    def start(self):
        log.info("Start Marquez server...")
        self._compose_executor.up()
        log.info(
            "Started Marquez server. Web UI: http://localhost:3000. "
            "To send lineage set VDK_OPENLINEAGE_URL=http://localhost:5002 ."
        )
        log.info("Opening Web UI: ")
        time.sleep(5)
        is_open = webbrowser.open("http://localhost:3000")
        if not is_open:
            log.warning(
                "Failed to open Web UI. Navigate manually to http://localhost:3000"
            )

    def stop(self):
        log.info("Stopping Marquez server...")
        self._compose_executor.down()
        log.info("Stopped Marquez server.")

    def check_status(self):
        output = self._compose_executor.execute("ps")
        log.info(output.decode("unicode_escape"))
