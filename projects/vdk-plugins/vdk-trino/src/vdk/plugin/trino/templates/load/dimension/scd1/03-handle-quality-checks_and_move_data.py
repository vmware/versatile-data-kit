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

"""
This step is intended to handle quality checks if such are provided
and stop the data from being populated into the target table if the check has negative outcome.
Otherwise the data will be directly processed according to the used template type
"""


def run(job_input: IJobInput):
    """
    2. Insert source view data to temp/staging table
    3. if check,
        - send temp/staging table for check validation
        - If validated,
            - drop target table and rename the temp/staging table to target table
        - else Raise error
    2. else,
        - drop target table and rename the temp/staging table to target table
    """

    job_arguments = job_input.get_arguments()

    check = job_arguments.get("check")
    source_schema = job_arguments.get("source_schema")
    source_view = job_arguments.get("source_view")
    target_schema = job_arguments.get("target_schema")
    target_table = job_arguments.get("target_table")

    # Insert source view data to temp/staging table
    create_table_and_insert_data_query = CommonUtilities.get_file_content(
        SQL_FILES_FOLDER, "02-create-table-and-insert-data.sql"
    )
    staging_schema = job_arguments.get("staging_schema", target_schema)
    staging_table = CommonUtilities.get_staging_table_name(target_schema, target_table)

    trino_queries = TrinoTemplateQueries(job_input)
    trino_queries.drop_table(db=target_schema, table_name=staging_table)

    # create staging table and  insert data into staging table
    create_staging_table_and_insert_data = create_table_and_insert_data_query.format(
        target_schema=staging_schema,
        target_table=staging_table,
        source_schema=source_schema,
        source_view=source_view,
    )
    job_input.execute_query(create_staging_table_and_insert_data)

    if check:
        staging_table_full_name = f"{staging_schema}.{staging_table}"
        if check(staging_table_full_name):
            overwrite_target_with_staging_table(
                trino_queries, target_schema, target_table, target_schema, staging_table
            )
        else:
            target_table_full_name = f"{target_schema}.{target_table}"
            raise DataQualityException(
                checked_object=staging_table_full_name,
                source_view=f"{source_schema}.{source_view}",
                target_table=target_table_full_name,
            )

    else:
        overwrite_target_with_staging_table(
            trino_queries, target_schema, target_table, target_schema, staging_table
        )


def overwrite_target_with_staging_table(
    trino_queries: TrinoTemplateQueries,
    target_schema,
    target_table,
    source_schema,
    source_table,
):
    # drop target table
    trino_queries.drop_table(target_schema, target_table)
    # rename the staging table to the target table
    trino_queries.rename_table(source_schema, source_table, target_schema, target_table)
