# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from logging import getLogger
from typing import cast
from typing import Type

from pydantic import BaseModel
from pydantic import ValidationError
from vdk.api.job_input import IJobInput
from vdk.internal.builtin_plugins.run.job_input import JobInput
from vdk.internal.core import errors
from vdk.plugin.impala.impala_helper import ImpalaHelper

log = getLogger(__name__)


class TemplateArgumentsValidator:
    TemplateParams: Type[BaseModel]

    def __init__(self) -> None:
        pass

    def get_validated_args(self, job_input: IJobInput, args: dict) -> dict:
        args.update(self._validate_args(args))
        args["_vdk_template_insert_partition_clause"] = ""

        impala_helper = ImpalaHelper(cast(JobInput, job_input).get_managed_connection())
        table_name = "`{target_schema}`.`{target_table}`".format(**args)
        table_description = impala_helper.get_table_description(table_name)
        partitions = impala_helper.get_table_partitions(table_description)
        if partitions:
            args[
                "_vdk_template_insert_partition_clause"
            ] = impala_helper.get_insert_sql_partition_clause(partitions)

        impala_helper.ensure_table_format_is_parquet(table_name, table_description)

        source_view_full_name = "`{source_schema}`.`{source_view}`".format(**args)
        raw_source_view_has_results = job_input.execute_query(
            """
            WITH limited_view AS (SELECT * FROM {} LIMIT 1)
            SELECT COUNT(1) > 0 FROM limited_view
            """.format(
                source_view_full_name
            )
        )
        source_view_has_results = raw_source_view_has_results[0][0]
        if not source_view_has_results:
            log.warning(
                "Source view returned no results. Source table is likely empty or non existent."
                + " Template will not be executed."
            )
            job_input.skip_remaining_steps()
        return args

    def _validate_args(self, args: dict) -> dict:
        try:
            return self.TemplateParams(**args).dict()
        except ValidationError as error:
            errors.log_and_rethrow(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=log,
                what_happened="Template execution in Data Job finished with error",
                why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(error),
                consequences=errors.MSG_CONSEQUENCE_TERMINATING_APP,
                countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION,
                exception=error,
            )
