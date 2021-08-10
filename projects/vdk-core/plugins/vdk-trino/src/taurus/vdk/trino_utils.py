# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.job_input import IJobInput
from taurus.vdk import trino_config
from taurus.vdk.core import errors
from trino.exceptions import TrinoUserError

log = logging.getLogger(__name__)


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

    def get_move_data_to_table_strategy(self):
        return trino_config.trino_templates_data_to_target_strategy

    def move_data_to_table(
        self, from_db: str, from_table_name: str, to_db: str, to_table_name: str
    ):
        """
        This method moves data from one table to another table, using different strategies, defined in job context
        configuration
        :param from_db: Schema of the table that we want to rename
        :param from_table_name: Name of the table we want to rename
        :param to_db: Schema of the new table we want
        :param to_table_name: Name of the new table
        :return: None if it fails, List if it succeeds
        """
        strategy = self.get_move_data_to_table_strategy()
        if strategy == "RENAME":
            return self.__job_input.execute_query(
                f"""
                ALTER TABLE {from_db}.{from_table_name} RENAME TO {to_db}.{to_table_name}
                """
            )
        elif strategy == "INSERT_SELECT":
            self.__job_input.execute_query(
                f"""
                CREATE TABLE {to_db}.{to_table_name} (LIKE {from_db}.{from_table_name})
                """
            )
            self.__job_input.execute_query(
                f"""
                INSERT INTO {to_db}.{to_table_name} SELECT * FROM {from_db}.{from_table_name}
                """
            )
            return self.__job_input.execute_query(
                f"""
                DROP TABLE {from_db}.{from_table_name}
                """
            )
        else:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=log,
                what_happened="Cannot move data to target",
                why_it_happened=f"Strategy for moving data to target table is not defined: {strategy}",
                consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail.",
                countermeasures="Provide valid value for TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY.",
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
