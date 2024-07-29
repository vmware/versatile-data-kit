# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os

from vdk.api.job_input import IJobInput
from vdk.plugin.trino.templates.data_quality_exception import DataQualityException
from vdk.plugin.trino.trino_utils import CommonUtilities

log = logging.getLogger(__name__)

SQL_FILES_FOLDER = (
    os.path.dirname(os.path.abspath(__file__)) + "/02-requisite-sql-scripts"
)

"""
This step is intened to handle quality checks if such provided
and stop the data from being populated into the target table if the check has negative outcome.
Otherwise the data will be directly processed according to the used template type
"""


def run(job_input: IJobInput):
    """
    1. create staging table
    2. Insert target table and source view data to staging_table using last_arrival_ts
    4. if check,
        - send staging table for check validation
        - If validated,
            - Use trino_utils function to move data from staging table to target table
        - else Raise error
    5. else,
        - check if tmp_target table has data
        - Use trino_utils function to move data from tmp target table to target table

    """

    job_arguments = job_input.get_arguments()

    check = job_arguments.get("check")
    source_schema = job_arguments.get("source_schema")
    source_view = job_arguments.get("source_view")
    target_schema = job_arguments.get("target_schema")
    target_table = job_arguments.get("target_table")
    last_arrival_ts = job_arguments.get("last_arrival_ts")
    drop_table_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-drop-table.sql"
    )
    create_table_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-create-table.sql"
    )
    create_table_and_insert_data_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-create-table-and-insert-data.sql"
    )
    insert_snapshot_data_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-insert-snapshot-data.sql"
    )

    staging_schema = job_arguments.get("staging_schema", target_schema)
    staging_table = CommonUtilities.get_staging_table_name(target_schema, target_table)

    staging_table_full_name = f"{staging_schema}.{staging_table}"
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

    # insert snapshot data
    insert_into_staging = insert_snapshot_data_query.format(
        staging_schema=staging_schema,
        staging_table=staging_table,
        target_schema=target_schema,
        target_table=target_table,
        source_schema=source_schema,
        source_view=source_view,
        last_arrival_ts=last_arrival_ts,
    )
    job_input.execute_query(insert_into_staging)

    # if validation check is selected
    if check and not check(staging_table_full_name):
        raise DataQualityException(
            checked_object=staging_table_full_name,
            source_view=f"{source_schema}.{source_view}",
            target_table=target_table_full_name,
        )
    else:
        log.debug("Check if staging table has data.")
        res = job_input.execute_query(
            f"""
                    SELECT COUNT(*) FROM {staging_schema}.{staging_table}
                    """
        )
        if res and res[0][0] > 0:
            log.debug(
                "Confirmed that staging table has data, proceed with moving it to target."
            )
            job_input.execute_query(drop_table_query)
            # insert into target
            create_and_insert_into_target = create_table_and_insert_data_query.format(
                target_schema=target_schema,
                target_table=target_table,
                source_schema=staging_schema,
                source_view=staging_table,
            )
            job_input.execute_query(create_and_insert_into_target)
        else:
            log.info(
                f"Target table {target_schema}.{target_table} remains unchanged "
                f"because source table {target_schema}.{source_view} was empty."
            )
