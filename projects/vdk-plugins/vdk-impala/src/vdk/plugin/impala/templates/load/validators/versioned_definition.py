# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from pydantic import BaseModel
from pydantic import validator
from vdk.api.job_input import IJobInput
from vdk.plugin.impala.templates.template_arguments_validator import (
    TemplateArgumentsValidator,
)


class LoadVersionedParams(BaseModel):
    target_schema: str
    target_table: str
    source_schema: str
    source_view: str
    id_column: str
    value_columns: List[str]
    tracked_columns: List[str]
    updated_at_column: str = "updated_at"
    sk_column: str = "sk"
    active_from_column: str = "active_from"
    active_to_column: str = "active_to"
    active_to_max_value: str = "9999-12-31"

    @validator("tracked_columns")
    def passwords_match(cls, tracked_columns, values, **kwargs):
        value_columns = values.get("value_columns")
        if type(value_columns) == list and not tracked_columns:
            raise ValueError("The list must contain at least one column")
        if type(value_columns) == list == type(value_columns) and not set(
            tracked_columns
        ) <= set(value_columns):
            raise ValueError(
                "All elements in the list must be also present in `value_columns`"
            )
        return tracked_columns


class LoadVersioned(TemplateArgumentsValidator):
    TemplateParams = LoadVersionedParams

    def __init__(self) -> None:
        super().__init__(
            template_name="load/versioned",
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

    def _validate_args(self, args: dict) -> dict:
        args = super()._validate_args(args)
        return dict(
            **args,
            value_columns_str=", ".join(
                [f"`{column}`" for column in args["value_columns"]]
            ),
            hash_expr_str=",\n".join(
                [
                    f"            COALESCE(CAST(`{column}` AS STRING), '#')"
                    for column in args["tracked_columns"]
                ]
            ).lstrip(),
        )


def get_validated_arguments(job_input: IJobInput):
    return LoadVersioned().get_validated_args(job_input, job_input.get_arguments())
