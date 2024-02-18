# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
import shlex
import subprocess
import tempfile
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from taurus_datajob_api import DataJobExecution
from vdk.internal.builtin_plugins.run.run_status import ExecutionStatus
from vdk.internal.builtin_plugins.run.summary_output import JobSummaryParser
from vdk.internal.core.error_classifiers import ResolvableBy
from vdk.plugin.dag.dags import IDataJobExecutor
from vdk.plugin.dag.remote_data_job import JobStatus

RUNNING_STATUSES = [JobStatus.RUNNING.value, JobStatus.SUBMITTED.value]


class LocalDataJob:
    def __init__(self, job_path: str, job_name: str, team_name: str, arguments: dict):
        self._job_name = job_name
        self._team_name = team_name
        self._job_path = job_path
        self._arguments = arguments

        temp_dir = os.path.join(tempfile.gettempdir(), "vdk-jobs", job_name)
        pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)
        self._log_file = os.path.join(temp_dir, "run.log")
        self._summary_file = os.path.join(temp_dir, "run-summary.json")
        self._log_file_handle = None
        self._process = None
        self._start_time = None
        self._end_time = None
        self._message = None

    def close(self):
        if self._log_file_handle:
            self._log_file_handle.close()
            self._log_file_handle = None
        if self._process:
            # Ensure the process has finished before closing
            self._process.wait()
            self._process = None

    def __del__(self):
        self.close()

    @staticmethod
    def __prepare_vdk_run_command(path: str, arguments: dict):
        path = shlex.quote(str(path))
        cmd: list[str] = ["vdk", "run", f"{path}"]
        if arguments:
            arguments = json.dumps(arguments)
            cmd.append("--arguments")
            cmd.append(f"{arguments}")
        return cmd

    def start_run(self):
        cmd = self.__prepare_vdk_run_command(self._job_path, self._arguments)

        environ_copy = os.environ.copy()
        environ_copy["JOB_RUN_SUMMARY_FILE_PATH"] = self._summary_file

        self._log_file_handle = pathlib.Path(self._log_file).open(mode="w+")

        self._process = subprocess.Popen(
            cmd,
            stdout=self._log_file_handle,
            stderr=self._log_file_handle,
            env=environ_copy,
            shell=False,
        )
        self._start_time = datetime.now()
        self._message = {"logs": self._log_file}
        return str(self._process.pid)

    def details(self) -> Dict:
        details = dict(
            start_time=self._start_time,
            end_time=self._end_time,
            status=self.status(),
            message=self._message,
            started_by="",
            type="local",
            deployment=None,
        )
        return details

    def status(self) -> str:
        if not self._process:
            return JobStatus.SUBMITTED.value

        result = self._process.poll()
        if result is None:
            return JobStatus.RUNNING.value

        if not self._end_time:
            self._end_time = datetime.now()

        if os.path.exists(self._summary_file):
            return self._determine_status_from_summary()
        else:
            return self._determine_status_without_summary(result)

    def _determine_status_from_summary(self) -> str:
        content = pathlib.Path(self._summary_file).read_text()
        job_summary = JobSummaryParser.from_json(content)

        if job_summary.status == ExecutionStatus.SUCCESS:
            return JobStatus.SUCCEEDED.value
        elif job_summary.status == ExecutionStatus.SKIP_REQUESTED:
            return JobStatus.SKIPPED.value
        else:
            # update with summary only in case of failure
            self._update_message_with_summary(content)
            if job_summary.blamee in (
                ResolvableBy.USER_ERROR,
                ResolvableBy.CONFIG_ERROR,
            ):
                return JobStatus.USER_ERROR.value
            else:
                return JobStatus.PLATFORM_ERROR.value

    def _determine_status_without_summary(self, result: int) -> str:
        if result != 0:
            # update with summary only in case of failure
            self._message = {"summary": {"exit_code": result}, "logs": self._log_file}
            return JobStatus.PLATFORM_ERROR.value
        else:
            return JobStatus.SUCCEEDED.value

    def _update_message_with_summary(self, content: str):
        self._message = json.loads(content)
        self._message["logs"] = self._log_file


class LocalDataJobRunException(Exception):
    def __init__(self, job_name: str, team_name: str, message: str):
        super().__init__(f"Data Job {job_name} of team {team_name}: {message}")
        self.job_name = job_name
        self.team_name = team_name


class LocalDataJobExecutor(IDataJobExecutor):
    """
    This module is responsible for executing local Data Jobs.
    """

    def __init__(self):
        self._running_jobs: Dict[str, LocalDataJob] = dict()

    @staticmethod
    def __find_job_path(job_name: str):
        candidates = [
            os.getcwd(),
        ]
        # TODO: expose this using the plugin configuration mechanisms (which infers also from env. vars among others)
        candidates += [
            part
            for part in os.environ.get("DAGS_LOCAL_RUN_JOB_PATH", "").split(":")
            if part
        ]

        for candidate in candidates:
            candidate_job_path = os.path.join(candidate, job_name)
            if os.path.isdir(candidate_job_path):
                return candidate_job_path

        raise LocalDataJobRunException(
            job_name, "", f"Cannot find the job directory. Search paths: {candidates}"
        )

    def start_job(
        self,
        job_name: str,
        team_name: str,
        started_by: str = None,
        arguments: dict = None,
    ):
        if job_name in self._running_jobs:
            raise LocalDataJobRunException(
                job_name,
                team_name,
                f"Job run already has been started. Cannot start same job twice.",
            )
        job_path = self.__find_job_path(job_name)

        job = LocalDataJob(
            job_path,
            job_name,
            team_name,
            arguments,
        )
        self._running_jobs[job_name] = job
        return job.start_run()

    def status_job(self, job_name: str, team_name: str, execution_id: str) -> str:
        if job_name in self._running_jobs:
            return self._running_jobs.get(job_name).status()
        else:
            return None  # TODO: or raise ?

    def details_job(self, job_name: str, team_name: str, execution_id: str) -> dict:
        if job_name in self._running_jobs:
            return self._running_jobs.get(job_name).details()
        else:
            return dict()  # TODO: or raise ?

    def job_executions_list(
        self, job_name: str, team_name: str
    ) -> Optional[List[DataJobExecution]]:
        return []
