# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os

from vdk.api.job_input import IJobInput
from vdk.plugin.trino.templates.data_quality_exception import DataQualityException
from vdk.plugin.trino.trino_utils import CommonUtilities

SQL_FILES_FOLDER = (
    os.path.dirname(os.path.abspath(__file__)) + "/02-requisite-sql-scripts"
)

log = logging.getLogger(__name__)

"""
This step is intened to handle quality checks if such provided
and stop the data from being populated into the target table if the check has negative outcome.
Otherwise the data will be directly processed according to the used template type
"""


def run(job_input: IJobInput):
    """
    1. if check,
        - create staging table
        - Insert  source view data to staging table
        - Drop view if exists
        - create view from union of staging table data and target table data
        - send view for check validation
        - If validated,
            - Append staging table data to target table data
            - drop view
        - else Raise error
    2. else,
        - append source view data to target table using insert query
    """
    job_arguments = job_input.get_arguments()

    check = job_arguments.get("check")
    source_schema = job_arguments.get("source_schema")
    source_view = job_arguments.get("source_view")
    target_schema = job_arguments.get("target_schema")
    target_table = job_arguments.get("target_table")
    create_table_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-create-table.sql"
    )
    create_view_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-create-consolidated-view.sql"
    )
    drop_table_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-drop-table.sql"
    )
    drop_view_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-drop-view.sql"
    )
    insert_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-insert-into-target.sql"
    )

    if check:
        staging_schema = job_arguments.get("staging_schema", target_schema)
        staging_table = CommonUtilities.get_staging_table_name(
            target_schema, target_table
        )

        target_table_full_name = f"{target_schema}.{target_table}"

        # drop table if exists
        drop_staging_table = drop_table_query.format(
            target_schema=staging_schema, target_table=staging_table
        )
        job_input.execute_query(drop_staging_table)

        # create staging table
        create_staging_table = create_table_query.format(
            table_schema=staging_schema,
            table_name=staging_table,
            target_schema=target_schema,
            target_table=target_table,
        )
        job_input.execute_query(create_staging_table)

        # insert data into staging table
        insert_into_staging = insert_query.format(
            source_schema=source_schema,
            source_view=source_view,
            target_schema=staging_schema,
            target_table=staging_table,
        )
        job_input.execute_query(insert_into_staging)

        view_schema = staging_schema
        view_name = f"vw_{staging_table}"
        # Drop view if already exist
        drop_view = drop_view_query.format(view_schema=view_schema, view_name=view_name)
        job_input.execute_query(drop_view)

        # create consolidated view of source and target table data using staging table
        create_view = create_view_query.format(
            view_schema=view_schema,
            view_name=view_name,
            staging_schema=staging_schema,
            staging_table=staging_table,
            target_schema=target_schema,
            target_table=target_table,
        )
        job_input.execute_query(create_view)

        view_full_name = f"{view_schema}.{view_name}"

        if check(view_full_name):
            insert_into_target = insert_query.format(
                source_schema=staging_schema,
                source_view=staging_table,
                target_schema=target_schema,
                target_table=target_table,
            )
            job_input.execute_query(insert_into_target)
            # drop view
            job_input.execute_query(drop_view)

        else:
            raise DataQualityException(
                checked_object=view_full_name,
                source_view=f"{source_schema}.{source_view}",
                target_table=target_table_full_name,
            )
    else:
        job_input.execute_query(insert_query)
