# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel
from vdk.api.job_input import IJobInput
from vdk.plugin.impala.templates.template_executor import TemplateExecutor


class FactDailySnapshotParams(BaseModel):
    target_schema: str
    target_table: str
    source_schema: str
    source_view: str
    last_arrival_ts: str


class FactDailySnapshot(TemplateExecutor):
    TemplateParams = FactDailySnapshotParams

    def __init__(self) -> None:
        super().__init__(
            template_name="load/fact/snapshot",
            sql_files=[
                "00-test-if-view-matches-target.sql",
                "01-insert-into-target.sql",
                "02-refresh.sql",
                "03-compute-stats.sql",
            ],
            sql_files_platform_is_responsible=[
                "02-refresh.sql",
                "03-compute-stats.sql",
            ],
        )


def run(job_input: IJobInput):
    FactDailySnapshot().start(job_input, job_input.get_arguments())
