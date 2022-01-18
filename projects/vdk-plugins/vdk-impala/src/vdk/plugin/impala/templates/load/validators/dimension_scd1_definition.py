# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel
from vdk.api.job_input import IJobInput
from vdk.plugin.impala.templates.template_executor import TemplateExecutor


class SlowlyChangingDimensionTypeOverwriteParams(BaseModel):
    target_schema: str
    target_table: str
    source_schema: str
    source_view: str


class SlowlyChangingDimensionTypeOverwrite(TemplateExecutor):
    TemplateParams = SlowlyChangingDimensionTypeOverwriteParams

    def __init__(self) -> None:
        super().__init__(
            template_name="scd1",
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
    return SlowlyChangingDimensionTypeOverwrite().start(
        job_input, job_input.get_arguments()
    )
