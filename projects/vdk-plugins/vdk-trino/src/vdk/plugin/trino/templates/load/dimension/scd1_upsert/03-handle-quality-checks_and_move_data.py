# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import re

from vdk.api.job_input import IJobInput
from vdk.plugin.trino.templates.data_quality_exception import DataQualityException
from vdk.plugin.trino.trino_utils import CommonUtilities

log = logging.getLogger(__name__)

SQL_FILES_FOLDER = (
    os.path.dirname(os.path.abspath(__file__)) + "/02-requisite-sql-scripts"
)


"""
This step is intended to handle quality checks if such are provided
and stop the data from being populated into the target table if the check has negative outcome.
Otherwise the data will be directly processed according to the used template type
"""


def run(job_input: IJobInput):
    """
    0. Drop staging table
    1. Insert target table data, upserted by source view data, to staging table
    2. if check,
        - send temp/staging table for check validation
        - If validated,
            - copy the data from staging to target table
        - else Raise error
        else,
        - copy the data from staging to target table
    3. Copying the data:
        - truncate target table and insert the data from staging table
    """

    job_arguments = job_input.get_arguments()

    check = job_arguments.get("check")
    source_schema = job_arguments.get("source_schema")
    source_view = job_arguments.get("source_view")
    target_schema = job_arguments.get("target_schema")
    target_table = job_arguments.get("target_table")
    id_column = job_arguments.get("id_column")

    staging_schema = job_arguments.get("staging_schema", target_schema)
    staging_table = CommonUtilities.get_staging_table_name(target_schema, target_table)

    # Drop staging table
    drop_table_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-drop-table.sql"
    )
    drop_table = drop_table_query.format(
        target_schema=staging_schema, target_table=staging_table
    )
    job_input.execute_query(drop_table)

    # create staging table and insert the source (new) data
    create_table_and_insert_data_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-create-table-and-insert-data.sql"
    )
    create_stg_tbl_and_insert_new_data = create_table_and_insert_data_query.format(
        source_schema=source_schema,
        source_view=source_view,
        target_schema_staging=staging_schema,
        target_table_staging=staging_table,
    )
    job_input.execute_query(create_stg_tbl_and_insert_new_data)

    staging_table_full_name = f"{staging_schema}.{staging_table}"

    # append the target-only (old) data to the staging table
    append_old_to_stg = f"""
        INSERT INTO {staging_table_full_name}
        SELECT t.*
        FROM {target_schema}.{target_table} AS t
        LEFT JOIN {staging_table_full_name} AS s ON s."{id_column}" = t."{id_column}"
        WHERE s."{id_column}" IS NULL
    """
    job_input.execute_query(append_old_to_stg)

    # copy the data if there's no quality check configure or if it passes
    if not check or check(staging_table_full_name):
        copy_staging_table_to_target_table(
            job_input, target_schema, target_table, staging_schema, staging_table
        )
    else:
        target_table_full_name = f"{target_schema}.{target_table}"
        raise DataQualityException(
            checked_object=staging_table_full_name,
            source_view=f"{source_schema}.{source_view}",
            target_table=target_table_full_name,
        )


def copy_staging_table_to_target_table(
    job_input: IJobInput,
    target_schema,
    target_table,
    source_schema,
    source_table,
):
    # non-partitioned tables:
    # - Since truncate and delete do not work for non-partitioned tables - get the create statement, drop the table and then re-create it - we do this to preserve and metadata like user comments
    # - Insert contents from staging table in target table
    # - Delete staging table
    show_create_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-show-create-table.sql"
    )
    show_create_target_table = show_create_query.format(
        target_schema=target_schema, target_table=target_table
    )

    table_create_statement = job_input.execute_query(show_create_target_table)
    # remove the "external_location" clause from the create statement as it might lead to data not being cleaned up properly in hive
    table_create_statement = remove_external_location(table_create_statement[0][0])

    # drop the table
    drop_table_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-drop-table.sql"
    )
    drop_table = drop_table_query.format(
        target_schema=target_schema, target_table=target_table
    )
    job_input.execute_query(drop_table)

    # re-create the table
    job_input.execute_query(table_create_statement)

    # insert the data
    insert_into_table_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-insert-into-table.sql"
    )
    insert_into_table = insert_into_table_query.format(
        target_schema=target_schema,
        target_table=target_table,
        source_schema=source_schema,
        source_table=source_table,
    )
    job_input.execute_query(insert_into_table)


def remove_external_location(sql_statement):
    # Regular expression pattern to match the external_location clause
    pattern = r"external_location\s*=\s*'[^']*',?\s*"

    # Remove the external_location clause from the SQL statement
    cleaned_sql = re.sub(pattern, "", sql_statement, flags=re.IGNORECASE)

    return cleaned_sql
