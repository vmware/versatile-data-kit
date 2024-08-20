# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os

from vdk.api.job_input import IJobInput
from vdk.plugin.trino.templates.data_quality_exception import DataQualityException
from vdk.plugin.trino.trino_utils import CommonUtilities
from vdk.plugin.trino.trino_utils import TrinoTemplateQueries

log = logging.getLogger(__name__)

SQL_FILES_FOLDER = (
    os.path.dirname(os.path.abspath(__file__)) + "/02-requisite-sql-scripts"
)

OVERWRITE = "OVERWRITE"

"""
This step is intended to handle quality checks if such are provided
and stop the data from being populated into the target table if the check has negative outcome.
Otherwise the data will be directly processed according to the used template type
"""


def run(job_input: IJobInput):
    """
    0. Drop staging table
    1. Insert source view data to staging table
    2. if check,
        - send temp/staging table for check validation
        - If validated,
            - copy the data from staging to target table
        - else Raise error
        else,
        - copy the data from staging to target table
    5. Copying the data:
        - if the table is partitioned: use Insert Overwrite from staging to target table
        - else: truncate target table and insert the data from staging table
    5. Drop staging table
    """

    job_arguments = job_input.get_arguments()

    check = job_arguments.get("check")
    source_schema = job_arguments.get("source_schema")
    source_view = job_arguments.get("source_view")
    target_schema = job_arguments.get("target_schema")
    target_table = job_arguments.get("target_table")

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

    # create staging table and insert data
    create_table_and_insert_data_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-create-table-and-insert-data.sql"
    )
    create_staging_table_and_insert_data = create_table_and_insert_data_query.format(
        target_schema=staging_schema,
        target_table=staging_table,
        source_schema=source_schema,
        source_view=source_view,
    )
    job_input.execute_query(create_staging_table_and_insert_data)

    try:
        staging_table_full_name = f"{staging_schema}.{staging_table}"

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
    finally:
        job_input.execute_query(drop_table)


def copy_staging_table_to_target_table(
    job_input: IJobInput,
    target_schema,
    target_table,
    source_schema,
    source_table,
):
    # check if table is partitioned
    if is_partitioned_table(job_input, target_schema, target_table):
        # If the table is partitioned, we are going to use insert overwrite: https://trino.io/docs/current/appendix/from-hive.html#overwriting-data-on-insert
        get_session_properties = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "02-get-session-properties.sql"
        )
        original_session_properties = job_input.execute_query(get_session_properties)
        original_session_properties_backup = []

        # Iterate over the original list of session properties
        for session_property in original_session_properties:
            # Store the property key and value as tuples
            original_session_properties_backup.append(
                (session_property[0], session_property[1])
            )

        set_session_property_template = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "02-set-session-property.sql"
        )
        try:
            # override session properties -> "SET SESSION hdfs.insert_existing_partitions_behavior = 'OVERWRITE';"
            for item in original_session_properties_backup:
                statement = set_session_property_template.format(
                    propety_name=item[0], property_value=OVERWRITE
                )
                job_input.execute_query(statement)

            # INSERT OVERWRITE data
            partition_clause = get_insert_sql_partition_clause(
                job_input, target_schema, target_table
            )

            insert_overwrite_query = CommonUtilities.get_file_content(
                SQL_FILES_FOLDER, "02-insert-overwrite.sql"
            )

            insert_overwrite = insert_overwrite_query.format(
                target_schema=target_schema,
                target_table=target_table,
                _vdk_template_insert_partition_clause=partition_clause,
                source_schema=source_schema,
                source_view=source_table,
            )
            job_input.execute_query(insert_overwrite)
        finally:
            # restore session properties
            for item in original_session_properties_backup:
                statement = set_session_property_template.format(
                    propety_name=item[0], property_value=item[1]
                )
                job_input.execute_query(statement)
    else:
        # non-partitioned tables:
        # - Truncate the target table
        # - Insert contents from staging table in target table
        # - Delete staging table
        truncate_table_query = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "02-truncate-table.sql"
        )
        truncate_table = truncate_table_query.format(
            target_schema=target_schema, target_table=target_table
        )
        job_input.execute_query(truncate_table)

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

        drop_table_query = CommonUtilities.get_file_content(
            SQL_FILES_FOLDER, "02-drop-table.sql"
        )
        drop_table = drop_table_query.format(
            target_schema=source_schema, target_table=source_table
        )
        job_input.execute_query(drop_table)


def is_partitioned_table(job_input: IJobInput, target_schema, target_table) -> bool:
    show_create_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-show-create-table.sql"
    )
    show_create_target_table = show_create_query.format(
        target_schema=target_schema, target_table=target_table
    )

    table_create_statement = job_input.execute_query(show_create_target_table)
    return (
        table_create_statement
        and table_create_statement[0][0]
        and "partitioned_by" in table_create_statement[0][0].lower()
    )


def get_insert_sql_partition_clause(job_input: IJobInput, target_schema, target_table):
    get_partitions_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-get-partitions.sql"
    )
    get_partitions = get_partitions_query.format(
        target_schema=target_schema, target_table=target_table
    )
    partitions_result = job_input.execute_query(get_partitions)

    partitions = []
    for partition in partitions_result:
        partitions.append(partition[0])

    sql = "PARTITION (" + ",".join("`" + p + "`" for p in partitions) + ")"
    return sql
