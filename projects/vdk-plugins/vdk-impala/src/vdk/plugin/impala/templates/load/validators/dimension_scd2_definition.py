# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel
from vdk.api.job_input import IJobInput
from vdk.plugin.impala.templates.template_executor import TemplateExecutor


class SlowlyChangingDimensionType2Params(BaseModel):
    target_schema: str
    target_table: str
    source_schema: str
    source_view: str
    start_time_column: str
    end_time_column: str
    end_time_default_value: str
    surrogate_key_column: str
    id_column: str


class SlowlyChangingDimensionType2(TemplateExecutor):
    TemplateParams = SlowlyChangingDimensionType2Params

    def __init__(self) -> None:
        super().__init__(
            template_name="load/dimension/scd2",
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


def validate_arguments(job_input: IJobInput):
    return SlowlyChangingDimensionType2().start(job_input, job_input.get_arguments())
