# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel
from vdk.api.job_input import IJobInput
from vdk.plugin.impala.templates.template_arguments_validator import (
    TemplateArgumentsValidator,
)


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


class SlowlyChangingDimensionType2(TemplateArgumentsValidator):
    TemplateParams = SlowlyChangingDimensionType2Params

    def __init__(self) -> None:
        super().__init__()


def run(job_input: IJobInput):
    SlowlyChangingDimensionType2().get_validated_args(
        job_input, job_input.get_arguments()
    )
