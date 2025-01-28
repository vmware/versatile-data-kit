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
    insert_query = get_file_content(SQL_FILES_FOLDER, "02-insert-into-target.sql")

    if check:
        staging_schema = job_arguments.get("staging_schema", target_schema)
        staging_table_name = get_staging_table_name(target_schema, target_table)

        staging_table = f"{staging_schema}.{staging_table_name}"
        target_table_full_name = f"{target_schema}.{target_table}"

        align_stg_table_with_target(target_table_full_name, staging_table, job_input)

        job_input.execute_query(f"TRUNCATE {staging_table}")

        insert_into_staging = insert_query.format(
            target_schema=staging_schema,
            target_table=staging_table_name,
            _vdk_template_insert_partition_clause=partition_clause,
            source_schema=source_schema,
            source_view=source_view,
        )
        job_input.execute_query(insert_into_staging)

        view_schema = staging_schema
        view_name = f"vw_{staging_table_name}"
        create_view_query = get_file_content(
            SQL_FILES_FOLDER, "02-create-consolidated-view.sql"
        )
        create_view = create_view_query.format(
            view_schema=view_schema,
            view_name=view_name,
            target_schema=target_schema,
            target_table=target_table,
            staging_schema=staging_schema,
            staging_table_name=staging_table_name,
        )
        job_input.execute_query(create_view)

        view_full_name = f"{view_schema}.{view_name}"
        if check(view_full_name):
            job_input.execute_query(f"COMPUTE STATS {staging_table}")

            insert_into_target = insert_query.format(
                source_schema=staging_schema,
                source_view=staging_table_name,
                _vdk_template_insert_partition_clause=partition_clause,
                target_schema=target_schema,
                target_table=target_table,
            )
            job_input.execute_query(insert_into_target)
        else:
            raise DataQualityException(
                checked_object=view_full_name,
                source_view=f"{source_schema}.{source_view}",
                target_table=target_table_full_name,
            )

    else:
        job_input.execute_query(insert_query)
