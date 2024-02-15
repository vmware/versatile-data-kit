# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import logging
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.run_status import ExecutionStatus
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.errors import ResolvableBy

log = logging.getLogger(__name__)

JOB_RUN_SUMMARY_FILE_PATH = "JOB_RUN_SUMMARY_FILE_PATH"


@dataclass(frozen=True)
class StepSummary:
    name: str
    status: ExecutionStatus | None
    blamee: ResolvableBy | None
    details: str | None


@dataclass(frozen=True)
class JobSummary:
    steps: list[StepSummary]
    status: ExecutionStatus | None
    blamee: ResolvableBy | None
    details: str | None


class JobSummaryParser:
    @staticmethod
    def to_json(job_summary: JobSummary) -> str:
        return json.dumps(asdict(job_summary))

    @staticmethod
    def __to_step_summary(data: dict[str, Any]) -> StepSummary:
        return StepSummary(
            name=data["name"],
            status=JobSummaryParser.__to_status(data.get("status")),
            blamee=JobSummaryParser.__to_blamee(data.get("blamee")),
            details=data.get("details", None),
        )

    @staticmethod
    def __to_status(data: str | None) -> ExecutionStatus:
        return ExecutionStatus(data) if data else None

    @staticmethod
    def __to_blamee(data: str | None) -> ResolvableBy:
        return ResolvableBy(data) if data else None

    @staticmethod
    def from_json(job_summary_sring: str) -> JobSummary:
        json_dict: dict = json.loads(job_summary_sring)
        json_steps = json_dict.get("steps", [])
        steps_list = [JobSummaryParser.__to_step_summary(step) for step in json_steps]

        job_summary = JobSummary(
            steps=steps_list,
            status=JobSummaryParser.__to_status(json_dict.get("status")),
            blamee=JobSummaryParser.__to_blamee(json_dict.get("blamee")),
            details=json_dict.get("details", None),
        )
        return job_summary


class JobRunSummaryOutputPlugin:
    @hookimpl
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        config_builder.add(
            key=JOB_RUN_SUMMARY_FILE_PATH,
            default_value="",
            description="The path location of the file where job run result summary is stored.",
        )

    @hookimpl(hookwrapper=True)
    def run_job(self, context: JobContext) -> None:
        out: HookCallResult
        out = yield

        output_path = context.core_context.configuration.get_value(
            JOB_RUN_SUMMARY_FILE_PATH
        )
        if output_path:
            log.debug(
                f"Summary output path is {output_path}. Will save job run summary there."
            )
            summary_infos = self._collect_job_summary(out.get_result())
            self._write_summary_to_file(summary_infos, output_path)

    @staticmethod
    def _write_summary_to_file(summary: JobSummary, output_path: str) -> None:
        with open(output_path, "w") as outfile:
            json_data = JobSummaryParser.to_json(job_summary=summary)
            outfile.write(json_data)

    @staticmethod
    def _collect_job_summary(result: ExecutionResult) -> JobSummary:
        steps = []
        for step_result in result.steps_list:
            step_summary = StepSummary(
                name=step_result.name,
                status=step_result.status,
                blamee=step_result.blamee,
                details=step_result.details,
            )
            steps.append(step_summary)
        job_summary = JobSummary(
            steps=steps,
            status=result.status,
            blamee=result.get_blamee(),
            details=result.get_details(),
        )
        return job_summary
