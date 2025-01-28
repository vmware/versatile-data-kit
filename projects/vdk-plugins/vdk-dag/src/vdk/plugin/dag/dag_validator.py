# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import graphlib
import json
import logging
from collections import namedtuple
from typing import Dict
from typing import List

from vdk.plugin.dag.exception import DagValidationException

log = logging.getLogger(__name__)
Error = namedtuple("Error", ["TYPE", "PERMISSION", "REQUIREMENT", "CONFLICT"])
ERROR = Error(
    TYPE="type", PERMISSION="permission", REQUIREMENT="requirement", CONFLICT="conflict"
)

allowed_job_keys = {
    "job_name",
    "team_name",
    "fail_dag_on_error",
    "depends_on",
    "arguments",
}
required_job_keys = {"job_name", "depends_on"}


class DagValidator:
    """
    The purpose of this class is to validate the DAG structure and jobs.
    It is being used right before the DAG is built.
    """

    def validate(self, jobs: List[Dict]):
        """
        Validate the structure and the order of the DAG of Data Jobs.

        :param jobs: List of Data Jobs (DAG vertices) to be validated
        :return:
        """
        self._validate_no_duplicates(jobs)
        for job in jobs:
            self._validate_job(job)
        self._check_dag_cycles(jobs)
        log.debug("Successfully validated the DAG!")

    def _validate_no_duplicates(self, jobs: List[Dict]):
        duplicated_jobs = list({job["job_name"] for job in jobs if jobs.count(job) > 1})
        if duplicated_jobs:
            raise DagValidationException(
                ERROR.CONFLICT,
                f"There are some duplicated jobs: {duplicated_jobs}.",
                f"Remove the duplicated jobs from the list - each job can appear in the jobs list at most once. "
                f"Duplicated jobs: {duplicated_jobs}.",
                duplicated_jobs,
            )

    def _validate_job(self, job: Dict):
        self._validate_job_type(job)
        self._validate_allowed_and_required_keys(job)
        self._validate_job_name(job)
        job_name = job.get("job_name")
        self._validate_dependencies(job_name, job["depends_on"])
        if "team_name" in job:
            self._validate_team_name(job_name, job["team_name"])
        if "fail_dag_on_error" in job:
            self._validate_fail_dag_on_error(job_name, job["fail_dag_on_error"])
        if "arguments" in job:
            self._validate_arguments(job_name, job["arguments"])
        log.debug(f"Successfully validated job: {job_name}")

    def _validate_job_type(self, job: Dict):
        if not isinstance(job, dict):
            jobs = ["".join(list(job))]
            raise DagValidationException(
                ERROR.TYPE,
                "The job type is not dict.",
                f"Change the Data Job type. Current type is {type(job)}. Expected type is dict.",
                jobs,
            )

    def _validate_allowed_and_required_keys(self, job: Dict):
        disallowed_keys = [key for key in job.keys() if key not in allowed_job_keys]
        if disallowed_keys:
            raise DagValidationException(
                ERROR.PERMISSION,
                "One or more job dict keys are not allowed.",
                f"Remove the disallowed Data Job Dict keys. "
                f"Keys {disallowed_keys} are not allowed. Allowed keys: {allowed_job_keys}.",
                None,
            )
        missing_keys = [key for key in required_job_keys if key not in job]
        if missing_keys:
            raise DagValidationException(
                ERROR.REQUIREMENT,
                "One or more job dict required keys are missing.",
                f"Add the missing required Data Job Dict keys. Keys {missing_keys} "
                f"are missing. Required keys: {required_job_keys}.",
                None,
            )

    def _validate_job_name(self, job: Dict):
        if not isinstance(job["job_name"], str):
            jobs = ["".join(list(job))]
            raise DagValidationException(
                ERROR.TYPE,
                "The type of the job dict key job_name is not string.",
                f"Change the Data Job Dict value of job_name. "
                f"Current type is {type(job['job_name'])}. Expected type is string.",
                jobs,
            )

    def _validate_dependencies(self, job_name: str, dependencies: List[str]):
        if not (isinstance(dependencies, List)):
            jobs = [job_name]
            raise DagValidationException(
                ERROR.TYPE,
                "The type of the job dict depends_on key is not list.",
                f"Check the Data Job Dict type of the depends_on key. Current type "
                f"is {type(dependencies)}. Expected type is list.",
                jobs,
            )
        non_string_dependencies = [
            pred for pred in dependencies if not isinstance(pred, str)
        ]
        if non_string_dependencies:
            jobs1 = [job_name]
            raise DagValidationException(
                ERROR.TYPE,
                "One or more items of the job dependencies list are not strings.",
                f"Check the Data Job Dict values of the depends_on list. "
                f"There are some non-string values: {non_string_dependencies}. Expected type is string.",
                jobs1,
            )

    def _validate_team_name(self, job_name: str, team_name: str):
        if not isinstance(team_name, str):
            jobs = [job_name]
            raise DagValidationException(
                ERROR.TYPE,
                "The type of the job dict key job_name is not string.",
                f"Change the Data Job Dict value of team_name. "
                f"Current type is {type(team_name)}. Expected type is string.",
                jobs,
            )

    def _validate_fail_dag_on_error(self, job_name: str, fail_dag_on_error: bool):
        if not isinstance(fail_dag_on_error, bool):
            jobs = [job_name]
            raise DagValidationException(
                ERROR.TYPE,
                "The type of the job dict key fail_dag_on_error is not bool (True/False).",
                f"Change the Data Job Dict value of fail_dag_on_error. Current type"
                f" is {type(fail_dag_on_error)}. Expected type is bool.",
                jobs,
            )

    def _validate_arguments(self, job_name: str, job_args: dict):
        if not isinstance(job_args, dict):
            jobs = [job_name]
            raise DagValidationException(
                ERROR.TYPE,
                "The type of the job dict key arguments is not dict.",
                f"Change the Data Job Dict value of arguments. "
                f"Current type is {type(job_args)}. Expected type is dict.",
                jobs,
            )
        try:
            json.dumps(job_args)
        except TypeError as e:
            reason = str(e)
            jobs1 = [job_name]
            raise DagValidationException(
                ERROR.TYPE,
                reason,
                f"Change the Data Job Dict value of arguments. "
                f"Current type is {type(job_args)} but not serializable as JSON.",
                jobs1,
            )

    def _check_dag_cycles(self, jobs: List[Dict]):
        topological_sorter = graphlib.TopologicalSorter()
        for job in jobs:
            topological_sorter.add(job["job_name"], *job["depends_on"])

        try:
            # Preparing the sorter raises CycleError if cycles exist
            topological_sorter.prepare()
        except graphlib.CycleError as e:
            jobs1 = e.args[1][:-1]
            raise DagValidationException(
                ERROR.CONFLICT,
                "There is a cycle in the DAG.",
                f"Change the depends_on list of the jobs that participate in the detected cycle: {e.args[1]}.",
                jobs1,
            )
