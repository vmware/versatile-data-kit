# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from collections import namedtuple
from typing import Dict
from typing import List

import graphlib
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import UserCodeError

log = logging.getLogger(__name__)
Error = namedtuple("Error", ["TYPE", "PERMISSION", "REQUIREMENT", "CONFLICT"])
ERROR = Error(
    TYPE="type", PERMISSION="permission", REQUIREMENT="requirement", CONFLICT="conflict"
)
allowed_job_keys = {
    "job_name",
    "team_name",
    "fail_meta_job_on_error",
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
        log.info("Successfully validated the DAG!")

    def _raise_error(
        self, jobs: List[Dict], error_type: str, reason: str, countermeasures: str
    ):
        raise UserCodeError(
            ErrorMessage(
                "",
                "Meta Job failed due to a Data Job validation failure.",
                f"There is a {error_type} error with job(s) {jobs}. " + reason,
                "The DAG will not be built and the Meta Job will fail.",
                countermeasures,
            )
        )

    def _validate_no_duplicates(self, jobs: List[Dict]):
        duplicated_jobs = list({job["job_name"] for job in jobs if jobs.count(job) > 1})
        if duplicated_jobs:
            self._raise_error(
                duplicated_jobs,
                ERROR.CONFLICT,
                f"There are some duplicated jobs: {duplicated_jobs}.",
                f"Remove the duplicated jobs from the list - each job can appear in the jobs list at most once. "
                f"Duplicated jobs: {duplicated_jobs}.",
            )

    def _validate_job(self, job: Dict):
        self._validate_allowed_and_required_keys(job)
        self._validate_job_name(job)
        self._validate_dependencies(job)
        self._validate_team_name(job)
        self._validate_fail_meta_job_on_error(job)
        self._validate_arguments(job)
        log.info(f"Successfully validated job: {job['job_name']}")

    def _validate_allowed_and_required_keys(self, job: Dict):
        forbidden_keys = [key for key in job.keys() if key not in allowed_job_keys]
        if forbidden_keys:
            self._raise_error(
                list(job),
                ERROR.PERMISSION,
                "One or more job dict keys are not allowed.",
                f"Remove the forbidden Data Job Dict keys. "
                f"Keys {forbidden_keys} are forbidden. Allowed keys: {allowed_job_keys}.",
            )
        missing_keys = [key for key in required_job_keys if key not in job]
        if missing_keys:
            self._raise_error(
                list(job),
                ERROR.REQUIREMENT,
                "One or more job dict required keys are missing.",
                f"Add the missing required Data Job Dict keys. Keys {missing_keys} "
                f"are missing. Required keys: {required_job_keys}.",
            )

    def _validate_job_name(self, job: Dict):
        if not isinstance(job["job_name"], str):
            self._raise_error(
                list(job),
                ERROR.TYPE,
                "The type of the job dict key job_name is not string.",
                f"Change the Data Job Dict value of job_name. "
                f"Current type is {type(job['job_name'])}. Expected type is string.",
            )

    def _validate_dependencies(self, job: Dict):
        if not (isinstance(job["depends_on"], List)):
            self._raise_error(
                list(job),
                ERROR.TYPE,
                "The type of the job dict depends_on key is not list.",
                f"Check the Data Job Dict type of the depends_on key. Current type "
                f"is {type(job['depends_on'])}. Expected type is list.",
            )
        non_string_dependencies = [
            pred for pred in job["depends_on"] if not isinstance(pred, str)
        ]
        if non_string_dependencies:
            self._raise_error(
                list(job),
                ERROR.TYPE,
                "One or more items of the job dependencies list are not strings.",
                f"Check the Data Job Dict values of the depends_on list. "
                f"There are some non-string values: {non_string_dependencies}. Expected type is string.",
            )

    def _validate_team_name(self, job: Dict):
        if "team_name" in job and not isinstance(job["team_name"], str):
            self._raise_error(
                list(job),
                ERROR.TYPE,
                "The type of the job dict key job_name is not string.",
                f"Change the Data Job Dict value of team_name. "
                f"Current type is {type(job['team_name'])}. Expected type is string.",
            )

    def _validate_fail_meta_job_on_error(self, job: Dict):
        if "fail_meta_job_on_error" in job and not isinstance(
            (job["fail_meta_job_on_error"]), bool
        ):
            self._raise_error(
                list(job),
                ERROR.TYPE,
                "The type of the job dict key fail_meta_job_on_error is not bool (True/False).",
                f"Change the Data Job Dict value of fail_meta_job_on_error. Current type"
                f" is {type(job['fail_meta_job_on_error'])}. Expected type is bool.",
            )

    def _validate_arguments(self, job: Dict):
        if "arguments" in job:
            if not isinstance(job["arguments"], dict):
                self._raise_error(
                    job["job_name"],
                    ERROR.TYPE,
                    "The type of the job dict key arguments is not dict.",
                    f"Change the Data Job Dict value of arguments. "
                    f"Current type is {type(job['arguments'])}. Expected type is dict.",
                )
            try:
                json.dumps(job["arguments"])
            except TypeError as e:
                self._raise_error(
                    list(job),
                    ERROR.TYPE,
                    str(e),
                    f"Change the Data Job Dict value of arguments. "
                    f"Current type is {type(job['arguments'])} but not serializable as JSON.",
                )

    def _check_dag_cycles(self, jobs: List[Dict]):
        topological_sorter = graphlib.TopologicalSorter()
        for job in jobs:
            topological_sorter.add(job["job_name"], *job["depends_on"])

        try:
            # Preparing the sorter raises CycleError if cycles exist
            topological_sorter.prepare()
        except graphlib.CycleError as e:
            self._raise_error(
                e.args[1][:-1],
                ERROR.CONFLICT,
                "There is a cycle in the DAG.",
                f"Change the depends_on list of the jobs that participate in the detected cycle: {e.args[1]}.",
            )
