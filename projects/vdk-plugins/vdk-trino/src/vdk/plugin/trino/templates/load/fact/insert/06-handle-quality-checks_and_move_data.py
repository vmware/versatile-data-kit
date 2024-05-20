# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os

from vdk.api.job_input import IJobInput
from vdk.plugin.trino.templates.data_quality_exception import DataQualityException
from vdk.plugin.trino.trino_utils import CommonUtilities
from vdk.plugin.trino.trino_utils import TrinoTemplateQueries

SQL_FILES_FOLDER = (
    os.path.dirname(os.path.abspath(__file__)) + "/06-requisite-sql-scripts"
)

log = logging.getLogger(__name__)

"""
This step is intened to handle quality checks if such provided
and stop the data from being populated into the target table if the check has negative outcome.
Otherwise the data will be directly processed according to the used template type
"""


def run(job_input: IJobInput):
    """
    1. Delete tmp_target and backup_target table if exist
    2. create tmp_target
    3. Insert target table and source view data to tmp_target
    4. if check,
        - create staging table
        - Use trino_utils function to move data from tmp_target to staging table
        - Drop view if exists
        - create view from staging table data
        - send view for check validation
        - If validated,
            - drop backup table
            - Use trino_utils function to move data from staging table to target table
        - else Raise error
    5. else,
        - check if tmp_target table has data
        - Use trino_utils function to move data from tmp target table to target table

    """
    job_arguments = job_input.get_arguments()

    check = job_arguments.get("check")
    trino_queries = TrinoTemplateQueries(job_input)
    source_schema = job_arguments.get("source_schema")
    source_view = job_arguments.get("source_view")
    target_schema = job_arguments.get("target_schema")
    target_table = job_arguments.get("target_table")
    backup_target_table = f"backup_{target_table}"
    tmp_target_table = f"tmp_{target_table}"

    if check:
        create_table_query = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "06-create-clone-table.sql"
        )
        create_view_query = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "06-create-consolidated-view.sql"
        )
        drop_table_query = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "06-drop-table.sql"
        )
        drop_view_query = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "06-drop-view.sql"
        )

        staging_schema = job_arguments.get("staging_schema", target_schema)
        staging_table_name = CommonUtilities.get_staging_table_name(
            target_schema, target_table
        )

        target_table_full_name = f"{target_schema}.{target_table}"

        # create staging table
        create_staging_table = create_table_query.format(
            table_schema=staging_schema,
            table_name=staging_table_name,
            target_schema=target_schema,
            target_table=target_table,
        )
        job_input.execute_query(create_staging_table)

        # use trino_utils function to move data
        trino_queries.perform_safe_move_data_to_table_step(
            from_db=target_schema,
            from_table_name=tmp_target_table,
            to_db=staging_schema,
            to_table_name=staging_table_name,
        )

        view_schema = staging_schema
        view_name = f"vw_{staging_table_name}"
        # Drop view if already exist
        drop_view = drop_view_query.format(view_schema=view_schema, view_name=view_name)
        job_input.execute_query(drop_view)

        # create consolidated view of source and target table data using staging table
        create_view = create_view_query.format(
            view_schema=view_schema,
            view_name=view_name,
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

            # Drop backup target if already exists
            drop_backup_target = drop_table_query.format(
                target_schema=target_schema, target_table=backup_target_table
            )
            job_input.execute_query(drop_backup_target)

            # use trino_utils function to move data
            trino_queries.perform_safe_move_data_to_table_step(
                from_db=staging_schema,
                from_table_name=staging_table_name,
                to_db=target_schema,
                to_table_name=target_table,
            )
            # drop view
            job_input.execute_query(drop_view)

        else:
            raise DataQualityException(
                checked_object=view_full_name,
                source_view=f"{source_schema}.{source_view}",
                target_table=target_table_full_name,
            )
    else:
        log.debug("Check if tmp target has data.")
        res = job_input.execute_query(
            f"""
            SELECT COUNT(*) FROM {target_schema}.{tmp_target_table}
            """
        )
        if res and res[0][0] > 0:
            log.debug(
                "Confirmed that tmp target has data, proceed with moving it to target."
            )
            trino_queries.perform_safe_move_data_to_table_step(
                from_db=target_schema,
                from_table_name=tmp_target_table,
                to_db=target_schema,
                to_table_name=target_table,
            )
        else:
            log.info(
                f"Target table {target_schema}.{target_table} remains unchanged "
                f"because source table {target_schema}.{source_view} was empty."
            )
            trino_queries.drop_table(target_schema, tmp_target_table)
