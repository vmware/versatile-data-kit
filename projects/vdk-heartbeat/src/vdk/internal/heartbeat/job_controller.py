# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import configparser
import json
import logging
import os
import shutil
import subprocess
import tempfile
import time

from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.tracing import LogDecorator

log = logging.getLogger(__name__)


class JobController:
    """
    Make sure to deploy data job.
    It uses vdkcli in order to test it as well.
    """

    def __init__(self, config: Config):
        self.config = config
        control_api_url_message = (
            config.control_api_url
            or "Not set (default from VDK's configuration will be used)"
        )
        auth_endpoint_message = (
            config.vdkcli_oauth2_uri
            or "Not set (default from VDK's configuration will be used)"
        )
        log.info(
            f"Using Control Service REST API URL: {control_api_url_message} "
            f"with job {config.job_name} and team {config.job_team}. "
            f"Authorization endpoint: {auth_endpoint_message}"
        )

    # If no value is found, argument will not be passed and default configuration will be used
    def __get_api_token_authorization_url_arg(self):
        if self.config.vdkcli_oauth2_uri:
            return ["-u", f"{self.config.vdkcli_oauth2_uri}"]
        else:
            return []

    # If no value is found, argument will not be passed and default configuration will be used
    def __get_rest_api_url_arg(self):
        if self.config.control_api_url:
            return ["-u", f"{self.config.control_api_url}"]
        else:
            return []

    # Set data job deployment to use a specific VDK version (if configured)
    def __get_vdk_version_arg(self):
        if self.config.deploy_job_vdk_version:
            return [
                "--update",
                "--vdk-version",
                f"{self.config.deploy_job_vdk_version}",
            ]
        else:
            return []

    def _execute(self, command):
        # base_command = [f"python", "-m", "vdk.internal.control.main"]
        base_command = [self.config.vdk_command_name]
        full_command = base_command + command
        log.debug(f"Command: {full_command}")
        try:
            os.environ.update(
                {
                    "VDK_OP_ID": self.config.op_id,
                    "VDK_OP_ID_OVERRIDE": self.config.op_id,
                }
            )
            out = subprocess.check_output(full_command)
            log.debug(f"out: {out}")
            return out
        except subprocess.CalledProcessError as process_error:
            log.exception(
                f"{full_command} failed. \nstdout: {process_error.stdout}, \nstderr: {process_error.stderr}"
            )
            raise

    @LogDecorator(log)
    def login(self):
        if self.config.vdkcli_api_refresh_token:
            self._execute(
                [
                    "login",
                    "-a",
                    f"{self.config.vdkcli_api_refresh_token}",
                    "-t",
                    "api-token",
                ]
                + self.__get_api_token_authorization_url_arg()
            )
        else:
            log.info("Running against control service without authentication.")

    @LogDecorator(log)
    def delete_job(self):
        self._execute(
            [
                "delete",
                "-n",
                self.config.job_name,
                "-t",
                self.config.job_team,
                "--yes",
            ]
            + self.__get_rest_api_url_arg()
        )

    @LogDecorator(log)
    def create_job(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._execute(
                [
                    "create",
                    "-n",
                    self.config.job_name,
                    "-t",
                    self.config.job_team,
                    "-p",
                    tmpdir,
                ]
                + self.__get_rest_api_url_arg()
            )

    @LogDecorator(log)
    def check_list_jobs(self):
        res = self._execute(
            [
                "list",
                "-o",
                "json",
                "-t",
                self.config.job_team,
            ]
            + self.__get_rest_api_url_arg()
        )
        res = json.loads(res)
        assert filter(
            lambda j: j["job_name"] == self.config.job_name, res
        ), f"list command missing created job {self.config.job_name}"

    @LogDecorator(log)
    def show_job_details(self):
        res = self._execute(
            [
                "show",
                "-o",
                "json",
                "-n",
                self.config.job_name,
                "-t",
                self.config.job_team,
            ]
            + self.__get_rest_api_url_arg()
        )
        res = json.loads(res)
        log.info(
            f"Team {self.config.job_team}, Job: {self.config.job_name} details: {json.dumps(res, indent=2)}"
        )

    @LogDecorator(log)
    def show_last_job_execution_logs(self):
        res = self._execute(
            [
                "execute",
                "--logs",
                "-n",
                self.config.job_name,
                "-t",
                self.config.job_team,
            ]
            + self.__get_rest_api_url_arg()
        )
        logs = res.decode("unicode_escape") if res else res
        log.info(
            f"Team {self.config.job_team}, Job: {self.config.job_name} Logs:\n {logs}"
        )

    @LogDecorator(log)
    def check_deployments(self, enabled=True, timeout_seconds=600):
        start = time.time()
        deployments = None
        while not deployments and time.time() - start < timeout_seconds:
            deployments = self._execute(
                [
                    "deploy",
                    "--show",
                    "-o",
                    "json",
                    "-n",
                    self.config.job_name,
                    "-t",
                    self.config.job_team,
                ]
                + self.__get_rest_api_url_arg()
            )
            deployments = json.loads(deployments)
            if not deployments:
                log.info("No deployments so far. Will wait 30 seconds and try again.")
                time.sleep(30)
        assert deployments, f"Job {self.config.job_name} deployment is missing"
        assert (
            deployments[0]["enabled"] == enabled
        ), f"Expected job {self.config.job_name} deploy flag enabled set to {enabled} but it is not."

    @LogDecorator(log)
    def get_job_properties(self):
        res = self._execute(
            [
                "properties",
                "--list",
                "-o",
                "json",
                "-n",
                self.config.job_name,
                "-t",
                self.config.job_team,
            ]
            + self.__get_rest_api_url_arg()
        )
        return json.loads(res)

    @LogDecorator(log)
    def set_job_property(self, key: str, value: str):
        self._execute(
            [
                "properties",
                "--set",
                key,
                value,
                "-n",
                self.config.job_name,
                "-t",
                self.config.job_team,
            ]
            + self.__get_rest_api_url_arg()
        )

    @LogDecorator(log)
    def enable_deployment_and_update_vdk_version(self):
        self._execute(
            [
                "deploy",
                "--enable",
                "-n",
                self.config.job_name,
                "-t",
                self.config.job_team,
            ]
            + self.__get_vdk_version_arg()
            + self.__get_rest_api_url_arg()
        )

    @LogDecorator(log)
    def disable_deployment(self):
        self._execute(
            [
                "deploy",
                "--disable",
                "-n",
                self.config.job_name,
                "-t",
                self.config.job_team,
            ]
            + self.__get_rest_api_url_arg()
        )

    @LogDecorator(log)
    def deploy_job(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            heartbeat_job_dir = self._get_data_job_dir(tmpdir)
            self._update_config_ini(heartbeat_job_dir)
            self._update_properties(heartbeat_job_dir)

            self._execute(
                [
                    "deploy",
                    "-n",
                    self.config.job_name,
                    "-t",
                    self.config.job_team,
                    "-p",
                    heartbeat_job_dir,
                    "-r",
                    "Updating heartbeat data job",
                ]
                + self.__get_rest_api_url_arg()
            )

    @LogDecorator(log)
    def start_job_execution(self):
        log.info("Starting data job execution through API.")
        job_execution = self._execute(
            [
                "execute",
                "--start",
                "-t",
                self.config.job_team,
                "-n",
                self.config.job_name,
                "-o",
                "json",
            ]
            + self.__get_rest_api_url_arg()
        )

        job_execution_id = json.loads(job_execution)["execution_id"]

        response = self._execute(
            [
                "execute",
                "--show",
                "-t",
                self.config.job_team,
                "-n",
                self.config.job_name,
                "-o",
                "json",
                "--execution-id",
                str(job_execution_id),
            ]
            + self.__get_rest_api_url_arg()
        )
        execution_response = json.loads(response)

        assert str(job_execution_id) in str(
            execution_response
        ), "Failed to start data job execution."
        log.info("Execution started successfully.")

    @LogDecorator(log)
    def check_job_execution_finished(self):
        log.info("Checking if data job execution is still running.")
        job_execution_running = True
        start = time.time()

        while (
            job_execution_running
            and time.time() - start < self.config.RUN_TEST_TIMEOUT_SECONDS
        ):
            response = self._execute(
                [
                    "execute",
                    "--list",
                    "-t",
                    self.config.job_team,
                    "-n",
                    self.config.job_name,
                    "-o" "json",
                ]
                + self.__get_rest_api_url_arg()
            )
            execution_list = json.loads(response)

            job_execution_running = False
            for execution in execution_list:
                if str(execution["status"]) == "running":
                    job_execution_running = True
                    log.info(
                        f"Data job execution is in state {execution['status']}. Will wait 10 seconds and check again."
                    )
                    break
            time.sleep(10)
        log.info(f"Data job is running : {job_execution_running}")
        assert not job_execution_running, (
            f"VDK-heartbeat timed out. Job execution {self.config.job_name} "
            + f"did not finish in {self.config.RUN_TEST_TIMEOUT_SECONDS}."
        )

    def _update_config_ini(self, heartbeat_job_dir):
        config_ini = configparser.ConfigParser()
        config_ini.add_section("owner")
        config_ini.add_section("job")
        config_ini.set("owner", "team", self.config.job_team)
        config_ini.set("job", "schedule_cron", "* * * * *")
        config_ini.set("job", "db_default_type", self.config.db_default_type)
        if self.config.job_notification_mail:
            config_ini.add_section("contacts")
            config_ini.set(
                "contacts", "notified_on_job_success", self.config.job_notification_mail
            )
            config_ini.set(
                "contacts", "notified_on_job_deploy", self.config.job_notification_mail
            )
            config_ini.set(
                "contacts",
                "notified_on_job_failure_user_error",
                self.config.job_notification_mail,
            )
            config_ini.set(
                "contacts",
                "notified_on_job_failure_platform_error",
                self.config.job_notification_mail,
            )
        with open(os.path.join(heartbeat_job_dir, "config.ini"), "w") as configfile:
            config_ini.write(configfile)

    def _get_data_job_dir(self, tmpdir):
        if self.config.data_job_directory_parent:
            vdk_heartbeat_data_job_path = self.config.data_job_directory_parent
        else:
            import vdk.internal.heartbeat.vdk_heartbeat_data_job

            vdk_heartbeat_data_job_path = (
                vdk.internal.heartbeat.vdk_heartbeat_data_job.__path__._path[0]
            )
        source_data_job_directory = os.path.abspath(
            os.path.join(
                vdk_heartbeat_data_job_path, self.config.data_job_directory_name
            )
        )
        heartbeat_temp_job_dir = os.path.join(tmpdir, "vdk-heartbeat-data-job")
        shutil.copytree(source_data_job_directory, heartbeat_temp_job_dir)
        cache_path = os.path.join(heartbeat_temp_job_dir, "__pycache__")
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
        return heartbeat_temp_job_dir

    def _update_properties(self, heartbeat_job_dir):
        python_script = f"""
def run(job_input):
    props = job_input.get_all_properties()
    props['db'] = "{self.config.DATABASE_TEST_DB}"
    props['table_source'] = "{self.config.DATABASE_TEST_TABLE_SOURCE}"
    props['table_destination'] = "{self.config.DATABASE_TEST_TABLE_DESTINATION}"
    props['table_load_destination'] = "{self.config.DATABASE_TEST_TABLE_LOAD_DESTINATION}"
    props['job_name'] = "{self.config.job_name}"
    props['execute_template'] = "{self.config.check_template_execution}"
    props['ingest_target'] = "{self.config.INGEST_TARGET}"
    props['ingest_method'] = "{self.config.INGEST_METHOD}"
    props['ingest_destination_table'] = "{self.config.INGEST_DESTINATION_TABLE}"
    props['ingest_timeout'] = "{self.config.INGEST_TIMEOUT}"
    job_input.set_all_properties(props)
        """

        with open(
            os.path.join(heartbeat_job_dir, "06_override_properties.py"), "w"
        ) as pyfile:
            pyfile.write(python_script)
