# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import re


def get_staging_table_name(target_schema, target_table):
    """
    Extracts staging table by given target schema and table.
    """
    staging_table_name = f"vdk_check_{target_schema}_{target_table}"

    if len(staging_table_name) > 128:
        raise ValueError(
            f"Staging table - {staging_table_name} exceeds the 128 character limit."
        )
    return staging_table_name


def get_file_content(sql_files_folder, sql_file_name):
    """
    Reads and returns file content by given path and file name.
    """
    query_full_path = os.path.join(sql_files_folder, sql_file_name)
    with open(query_full_path) as query:
        content = query.read()
        return content


def align_stg_table_with_target(target_table, stg_table, job_input):
    """
    Aligns structure of a given staging table with the structure of a given target table.
    """
    _create_table_like(target_table, stg_table, job_input)

    orig_create_table_statement = _extract_create_table_statement(
        target_table, job_input
    )
    clone_create_table_statement = _extract_create_table_statement(stg_table, job_input)

    if orig_create_table_statement != clone_create_table_statement:
        job_input.execute_query(f"DROP TABLE {stg_table}")
        _create_table_like(target_table, stg_table, job_input)


def _extract_create_table_statement(table_name, job_input):
    statement = job_input.execute_query(f"SHOW CREATE TABLE {table_name}")[0][0]
    statement = _remove_location(statement)
    statement = _remove_table_properties(statement)
    statement = _remove_create_table_prefix(statement)
    return statement


def _create_table_like(orig_table_name, clone_table_name, job_input):
    job_input.execute_query(
        f"CREATE TABLE IF NOT EXISTS {clone_table_name} LIKE {orig_table_name}"
    )


def _remove_location(create_table_statement):
    return re.sub(r"\s+LOCATION '[^']'", "", create_table_statement)


def _remove_create_table_prefix(create_table_statement):
    return re.sub("^CREATE TABLE[^\\(]*\\(", "", create_table_statement)


def _remove_table_properties(create_table_statement):
    return re.sub("\\s+TBLPROPERTIES \\([^\\)]*\\)", "", create_table_statement)
