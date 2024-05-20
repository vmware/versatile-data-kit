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
    job_arguments = job_input.get_arguments()

    check = job_arguments.get("check")
    if check:
        source_schema = job_arguments.get("source_schema")
        source_view = job_arguments.get("source_view")
        target_schema = job_arguments.get("target_schema")
        target_table = job_arguments.get("target_table")
        insert_query = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "02-insert-into-target.sql"
        )
        create_table_query = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "02-create-clone-table.sql"
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

        staging_schema = job_arguments.get("staging_schema", target_schema)
        staging_table_name = CommonUtilities.get_staging_table_name(
            target_schema, target_table
        )

        target_table_full_name = f"{target_schema}.{target_table}"

        # Drop table if already exists
        drop_staging_table = drop_table_query.format(
            target_schema=staging_schema, target_table=staging_table_name
        )
        job_input.execute_query(drop_staging_table)
        # create staging table with exact schema of target table
        create_staging_table = create_table_query.format(
            table_schema=staging_schema,
            table_name=staging_table_name,
            target_schema=target_schema,
            target_table=target_table,
        )
        job_input.execute_query(create_staging_table)
        # insert all source_view data into staging table
        insert_into_staging = insert_query.format(
            target_schema=staging_schema,
            target_table=staging_table_name,
            source_schema=source_schema,
            source_view=source_view,
        )
        job_input.execute_query(insert_into_staging)

        view_schema = staging_schema
        view_name = f"vw_{staging_table_name}"
        # Drop view if already exist
        drop_view = drop_view_query.format(view_schema=view_schema, view_name=view_name)
        job_input.execute_query(drop_view)

        # create consolidated view of staging and target table
        create_view = create_view_query.format(
            view_schema=view_schema,
            view_name=view_name,
            target_schema=target_schema,
            target_table=target_table,
            staging_schema=staging_schema,
            staging_table=staging_table_name,
        )
        job_input.execute_query(create_view)

        view_full_name = f"{view_schema}.{view_name}"

        if check(view_full_name):
            job_input.execute_query(
                f"SELECT * FROM "
                f"information_schema.tables WHERE table_schema = '{staging_schema}' "
                f"AND table_name = '{staging_table_name}'"
            )
            log.debug("Data View is created successfully.")
        else:
            raise DataQualityException(
                checked_object=view_full_name,
                source_view=f"{source_schema}.{source_view}",
                target_table=target_table_full_name,
            )
