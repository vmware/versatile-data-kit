# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from typing import List
from typing import Optional

from vdk.internal.core.error_classifiers import ResolvableBy
from vdk.internal.core.error_classifiers import ResolvableByActual
from vdk.internal.core.errors import BaseVdkError


class DagValidationException(BaseVdkError):
    """
    Exception raised for errors during DAG data job validation.

    :param error_type: The type of error encountered.
    :param reason: Explanation of why the error occurred.
    :param countermeasures: Suggested actions to resolve the error.
    :param jobs: List of jobs associated with the error, defaults to None.
    """

    def __init__(
        self, error_type: str, reason: str, countermeasures: str, jobs: List[str] = None
    ):
        self.jobs = jobs if jobs is not None else []
        self.error_type = error_type
        self.reason = reason
        self.countermeasures = countermeasures

        jobs_formatted = ", ".join(self.jobs) if self.jobs else "N/A"
        message = (
            f"DAG Validation Error:\n"
            f"  - Error Type: {self.error_type}\n"
            f"  - Affected Jobs: {jobs_formatted}\n"
            f"  - Reason: {self.reason}\n"
            f"  - Countermeasures: {self.countermeasures}"
        )
        super().__init__(ResolvableByActual.USER, ResolvableBy.USER_ERROR, message)


class DagJobExecutionException(BaseVdkError):
    """
    Exception raised when an execution of a job within a DAG fails.

    :param str job_name: The name of the job that failed.
    :param dict details: Any details relevant to the failure, optional.
    """

    def __init__(self, job_name: str, details: Optional[dict] = None):
        self.job_name = job_name
        self.details = details if details is not None else {}

        details_formatted = self.format_details(self.details)

        message = (
            f"Failure in DAG execution - Job '{self.job_name}' failed.\n"
            f"  - Failed Job details:\n{details_formatted}"
        )
        # regardless of the failed job resolvable type, the DAG job always fails with user error
        # since the DAG itself didn't fail due to platform error.
        # The failed job itself might be platform error in this case the platform would still be alerted.
        # While the user is responsible for looking at the DAG itself.
        super().__init__(ResolvableByActual.USER, ResolvableBy.USER_ERROR, message)

    @staticmethod
    def format_details(details: dict) -> str:
        if not details:
            return "None"

        def format_dict(d, indent=0, indent_prefix="  ", initial_prefix="    "):
            formatted_str = ""
            current_indent = initial_prefix + indent_prefix * indent
            for key, value in d.items():
                if not value:
                    continue
                formatted_str += f"{current_indent}{key}: "
                if isinstance(value, dict) and indent < 1:
                    # Print nested dictionaries only up to the 2nd level
                    formatted_str += "\n" + format_dict(
                        value, indent + 1, indent_prefix
                    )
                else:
                    formatted_str += f"{value}\n"
            return formatted_str

        return format_dict(details)
