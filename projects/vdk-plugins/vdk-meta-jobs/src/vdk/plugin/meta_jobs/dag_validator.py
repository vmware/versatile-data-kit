# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from collections import namedtuple
from typing import Dict
from typing import List

from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import UserCodeError

log = logging.getLogger(__name__)
Error = namedtuple("Error", ["TYPE", "PERMISSION", "REQUIREMENT", "CONFLICT"])
ERROR = Error(
    TYPE="type", PERMISSION="permission", REQUIREMENT="requirement", CONFLICT="conflict"
)
allowed_job_keys = ["job_name", "team_name", "fail_meta_job_on_error", "depends_on"]
required_job_keys = ["job_name", "depends_on"]


class DagValidator:
    def validate(self, jobs: List[Dict]):
        validated_jobs = list()
        for job in jobs:
            validated_jobs = self._validate_job(job, validated_jobs)

    def _raise_error(self, job, error_type, countermeasures):
        raise UserCodeError(
            ErrorMessage(
                "",
                "Meta Job failed due to a data job validation failure.",
                f"There is a {error_type} error with job {job}.",
                "The DAG will not be built and the meta data job will fail.",
                countermeasures,
            )
        )

    def _validate_job(self, job: Dict, validated_jobs):
        self._validate_allowed_and_required_keys(job)
        self._validate_job_name(job, validated_jobs)
        self._validate_dependencies(job, validated_jobs)
        self._validate_team_name(job)
        self._validate_fail_meta_job_on_error(job)
        log.info(f"Successfully validated job: {job['job_name']}")
        validated_jobs.append(job["job_name"])
        return validated_jobs

    def _validate_allowed_and_required_keys(self, job):
        if any(key not in allowed_job_keys for key in job.keys()):
            forbidden_keys = [key not in allowed_job_keys for key in job.keys()]
            self._raise_error(
                job,
                ERROR.PERMISSION,
                f"Remove the forbidden Data Job keys. "
                f"Keys {forbidden_keys} are forbidden. Allowed keys: {allowed_job_keys}.",
            )
        if any(key not in job for key in required_job_keys):
            missing_keys = [key not in job for key in required_job_keys]
            self._raise_error(
                job,
                ERROR.REQUIREMENT,
                f"Add the missing required Data Job keys. Keys {missing_keys} "
                f"are missing. Required keys: {required_job_keys}.",
            )

    def _validate_job_name(self, job, validated_jobs):
        if not isinstance(job["job_name"], str):
            self._raise_error(
                job,
                ERROR.TYPE,
                f"Change the Data Job Dict value of job_name. "
                f"Current type is {type(job['job_name'])}. Expected type is string.",
            )
        if validated_jobs is not None and job["job_name"] in validated_jobs:
            self._raise_error(
                job,
                ERROR.TYPE,
                f"Change the Data Job Dict value of job_name. "
                f"Job with name {job['job_name']} already exists.",
            )

    def _validate_dependencies(self, job, validated_jobs):
        if not (isinstance(job["depends_on"], list)):
            self._raise_error(
                job,
                ERROR.TYPE,
                f"Check the Data Job Dict value of depends_on. Current type "
                f"is {type(job['depends_on'])}. Expected type is list.",
            )
        if not all(isinstance(pred, str) for pred in job["depends_on"]):
            self._raise_error(
                job,
                ERROR.TYPE,
                f"Check the Data Job Dict values of the depends_on list. "
                f"There are some non-string values: "
                f"{[pred for pred in job['depends_on'] if not isinstance(pred, str)]}. "
                f"Expected type is string.",
            )
        if validated_jobs is not None and any(
            pred not in validated_jobs for pred in job["depends_on"]
        ):
            self._raise_error(
                job,
                ERROR.CONFLICT,
                f"Check the Data Job Dict dependencies. The DAG order is not topologically correct. "
                f"The following job dependencies are expected to be already validated but are not: "
                f"{[pred not in validated_jobs for pred in job['depends_on']]}.",
            )

    def _validate_team_name(self, job):
        if "team_name" in job and not isinstance(job["team_name"], str):
            self._raise_error(
                job,
                ERROR.TYPE,
                f"Change the Data Job Dict value of team_name. "
                f"Current type is {type(job['team_name'])}. Expected type is string.",
            )

    def _validate_fail_meta_job_on_error(self, job):
        if "fail_meta_job_on_error" in job and not isinstance(
            (job["fail_meta_job_on_error"]), bool
        ):
            self._raise_error(
                job,
                ERROR.TYPE,
                f"Change the Data Job Dict value of fail_meta_job_on_error. Current type"
                f" is {type(job['fail_meta_job_on_error'])}. Expected type is bool.",
            )
