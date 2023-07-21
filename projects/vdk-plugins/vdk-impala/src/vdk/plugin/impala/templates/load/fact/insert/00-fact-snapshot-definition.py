# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Callable
from typing import Optional

from pydantic import BaseModel
from vdk.api.job_input import IJobInput
from vdk.plugin.impala.templates.template_arguments_validator import (
    TemplateArgumentsValidator,
)


class FactDailySnapshotParams(BaseModel):
    target_schema: str
    target_table: str
    source_schema: str
    source_view: str
    check: Optional[Callable[[str], bool]] = None
    staging_schema: Optional[str] = None


class FactDailySnapshot(TemplateArgumentsValidator):
    TemplateParams = FactDailySnapshotParams

    def __init__(self) -> None:
        super().__init__()


def run(job_input: IJobInput):
    FactDailySnapshot().get_validated_args(job_input, job_input.get_arguments())
