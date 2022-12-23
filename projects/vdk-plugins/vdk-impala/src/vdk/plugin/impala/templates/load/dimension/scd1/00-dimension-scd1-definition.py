# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel
from vdk.api.job_input import IJobInput
from typing import Callable
from typing import Optional
from vdk.plugin.impala.templates.template_arguments_validator import (
    TemplateArgumentsValidator,
)


class SlowlyChangingDimensionTypeOverwriteParams(BaseModel):
    target_schema: str
    target_table: str
    source_schema: str
    source_view: str
    check: Optional[Callable[[str], bool]]
    staging_schema: Optional[str]


class SlowlyChangingDimensionTypeOverwrite(TemplateArgumentsValidator):
    TemplateParams = SlowlyChangingDimensionTypeOverwriteParams

    def __init__(self) -> None:
        super().__init__()


def run(job_input: IJobInput):
    SlowlyChangingDimensionTypeOverwrite().get_validated_args(
        job_input, job_input.get_arguments()
    )
