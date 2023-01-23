# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import re

from vdk.api.job_input import IJobInput

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
    staging_schema = job_arguments.get("staging_schema", target_schema)
    insert_query = get_query("02-insert-into-target.sql")
    staging_table_name = f"vdk_check_{target_table}"

    if check:
        if not staging_schema:
            raise ValueError(
                "No staging_schema specified to execute the defined data checks against."
            )

        staging_table = f"{staging_schema}.{staging_table_name}"
        align_stg_table_with_target(
            f"{target_schema}.{target_table}", staging_table, job_input
        )

        insert_into_staging = insert_query.format(
            target_schema=staging_schema,
            target_table=staging_table_name,
            _vdk_template_insert_partition_clause=partition_clause,
            source_schema=source_schema,
            source_view=source_view,
        )
        job_input.execute_query(insert_into_staging)

        if check(staging_table):
            insert_into_target = insert_query.format(
                source_schema=staging_schema,
                source_view=staging_table_name,
                _vdk_template_insert_partition_clause=partition_clause,
                target_schema=target_schema,
                target_table=target_table,
            )
            job_input.execute_query(insert_into_target)
        else:
            raise Exception("The data is not passing the quality checks!")

    else:
        job_input.execute_query(insert_query)


def get_query(sql_file_name):
    query_full_path = os.path.join(SQL_FILES_FOLDER, sql_file_name)
    with open(query_full_path) as query:
        content = query.read()
        return content


def align_stg_table_with_target(target_table, stg_table, job_input):
    create_table_like(target_table, stg_table, job_input)

    orig_create_table_statement = extract_create_table_statement(
        target_table, job_input
    )
    clone_create_table_statement = extract_create_table_statement(stg_table, job_input)

    if orig_create_table_statement != clone_create_table_statement:
        job_input.execute_query(f"DROP TABLE {stg_table}")
        create_table_like(target_table, stg_table, job_input)


def extract_create_table_statement(table_name, job_input):
    statement = job_input.execute_query(f"SHOW CREATE TABLE {table_name}")[0][0]
    statement = remove_location(statement)
    statement = remove_table_properties(statement)
    statement = remove_create_table_prefix(statement)
    return statement


def create_table_like(orig_table_name, clone_table_name, job_input):
    job_input.execute_query(
        f"CREATE TABLE IF NOT EXISTS {clone_table_name} LIKE {orig_table_name}"
    )


def remove_location(create_table_statement):
    return re.sub(r"\s+LOCATION '[^']'", "", create_table_statement)


def remove_create_table_prefix(create_table_statement):
    return re.sub("^CREATE TABLE[^\\(]*\\(", "", create_table_statement)


def remove_table_properties(create_table_statement):
    return re.sub("\\s+TBLPROPERTIES \\([^\\)]*\\)", "", create_table_statement)
