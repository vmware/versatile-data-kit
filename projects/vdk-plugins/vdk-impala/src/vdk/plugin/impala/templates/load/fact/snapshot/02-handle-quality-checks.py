# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os

from vdk.api.job_input import IJobInput
from vdk.plugin.impala.templates.data_quality_exception import DataQualityException
from vdk.plugin.impala.templates.utility import align_stg_table_with_target
from vdk.plugin.impala.templates.utility import get_file_content
from vdk.plugin.impala.templates.utility import get_staging_table_name

SQL_FILES_FOLDER = (
    os.path.dirname(os.path.abspath(__file__)) + "/02-requisite-sql-scripts"
)

"""
This step is intened to handle quality checks if such provided
and stop the data from being populated into the target table if the check has negative outcome.
Otherwise the data will be directly processed according to the used template type
"""


def run(job_input: IJobInput):
    job_arguments = job_input.get_arguments()

    check = job_arguments.get("check")
    partition_clause = job_arguments["_vdk_template_insert_partition_clause"]
    source_schema = job_arguments.get("source_schema")
    source_view = job_arguments.get("source_view")
    target_schema = job_arguments.get("target_schema")
    target_table = job_arguments.get("target_table")
    last_arrival_ts = job_arguments.get("last_arrival_ts")
    insert_query = get_file_content(SQL_FILES_FOLDER, "02-insert-into-target.sql")
    overwrite_target_query = get_file_content(
        SQL_FILES_FOLDER, "02-overwrite-target.sql"
    )

    if check:
        staging_schema = job_arguments.get("staging_schema", target_schema)
        staging_table_name = get_staging_table_name(target_schema, target_table)

        staging_table = f"{staging_schema}.{staging_table_name}"
        target_table_full_name = f"{target_schema}.{target_table}"

        align_stg_table_with_target(target_table_full_name, staging_table, job_input)

        insert_into_staging = insert_query.format(
            current_target_schema=staging_schema,
            current_target_table=staging_table_name,
            target_schema=target_schema,
            target_table=target_table,
            _vdk_template_insert_partition_clause=partition_clause,
            source_schema=source_schema,
            source_view=source_view,
            last_arrival_ts=last_arrival_ts,
        )
        job_input.execute_query(insert_into_staging)

        if check(staging_table):
            job_input.execute_query(f"COMPUTE STATS {staging_table}")

            insert_into_target = overwrite_target_query.format(
                staging_schema=staging_schema,
                staging_table_name=staging_table_name,
                _vdk_template_insert_partition_clause=partition_clause,
                target_schema=target_schema,
                target_table=target_table,
            )
            job_input.execute_query(insert_into_target)
        else:
            raise DataQualityException(
                checked_object=staging_table,
                source_view=f"{source_schema}.{source_view}",
                target_table=target_table_full_name,
            )

    else:
        insert_query = insert_query.replace(
            "{current_target_schema}.{current_target_table}",
            f"{target_schema}.{target_table}",
        )
        job_input.execute_query(insert_query)
