# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.api.job_input import IJobInput
from trino.exceptions import TrinoUserError


class TrinoQueries:
    """
    Allows to execute queries against Trino for a concrete job_input more easily.
    Provides a table_exists method (a command that Trino does not support).
    """

    def __init__(self, job_input: IJobInput):
        self.__job_input = job_input

    def table_exists(self, db: str, table_name: str) -> bool:
        """
        This method uses DESCRIBE command to check if a table exists.
        :param db: The name of the schema in which the table is
        :param table_name: The name of the table we want to check
        :return: True or False
        """
        result = True
        try:
            self.__job_input.execute_query(f"DESCRIBE {db}.{table_name}")
        except Exception as e:
            if self.__is_table_not_found_error(e):
                result = False
                pass
            else:
                raise

        return result

    def alter_table(
        self, from_db: str, from_table_name: str, to_db: str, to_table_name: str
    ):
        """
        This method renames a table
        :param from_db: Schema of the table that we want to rename
        :param from_table_name: Name of the table we want to rename
        :param to_db: Schema of the new table we want
        :param to_table_name: Name of the new table
        :return: None if it fails, List if it succeeds
        """
        return self.__job_input.execute_query(
            f"""
            ALTER TABLE {from_db}.{from_table_name} RENAME TO {to_db}.{to_table_name}
            """
        )

    def drop_table(self, db: str, table_name: str):
        """
        This method drops a table if it exists
        :param db: Schema of the table
        :param table_name: Name if the table
        :return: None if it fails, List if it succeeds
        """
        return self.__job_input.execute_query(
            f"""
            DROP TABLE IF EXISTS {db}.{table_name}
            """
        )

    @staticmethod
    def __is_table_not_found_error(exception):
        return (
            isinstance(exception, TrinoUserError)
            and exception.error_name == "TABLE_NOT_FOUND"
        )
