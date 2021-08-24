# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.job_input import IJobInput
from taurus.vdk import trino_config
from taurus.vdk.core import errors
from trino.exceptions import TrinoUserError

log = logging.getLogger(__name__)


class TrinoTemplateQueries:
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
            self.__job_input.execute_query(
                f"""
                DESCRIBE "{db}"."{table_name}"
                """
            )
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
                ALTER TABLE "{from_db}"."{from_table_name}" RENAME TO "{to_db}"."{to_table_name}"
                """
            )
        elif strategy == "INSERT_SELECT":
            self.__job_input.execute_query(
                f"""
                CREATE TABLE "{to_db}"."{to_table_name}" (LIKE "{from_db}"."{from_table_name}")
                """
            )
            self.__job_input.execute_query(
                f"""
                INSERT INTO "{to_db}"."{to_table_name}" SELECT * FROM "{from_db}"."{from_table_name}"
                """
            )
            return self.__job_input.execute_query(
                f"""
                DROP TABLE "{from_db}"."{from_table_name}"
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
            DROP TABLE IF EXISTS "{db}"."{table_name}"
            """
        )

    def ensure_target_exists_step(self, db: str, target_name: str):
        """
        This method checks if target exists. If it does not, an attempt to recover it from backup is initiated.
        If there is no valid target at the end, error is raised.
        :param db: Schema of the target table
        :param target_name: Name of the target table
        :return: None
        """
        backup_name = self.__get_backup_table_name(target_name)
        if not self.table_exists(db, target_name):
            log.debug("If there is backup, try to recover target from it")
            if self.table_exists(db, backup_name):
                log.debug("Try to recover target from backup")
                try:
                    self.move_data_to_table(db, backup_name, db, target_name)
                    log.info(
                        f"""Successfully recovered {db}.{target_name} from {db}.{backup_name}"""
                    )
                except Exception as e:
                    errors.log_and_throw(
                        to_be_fixed_by=errors.ResolvableBy.PLATFORM_ERROR,
                        log=log,
                        what_happened=f"""Target table is unexistent and recovering it from backup table failed with "
                                      "exception: {e}""",
                        why_it_happened=f"""One of the previous job retries failed after dropping "
                        "{db}.{target_name} and before moving data to it.""",
                        consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail.",
                        countermeasures=f"""You could try to recover {db}.{target_name} from"
                                        "{db}.{backup_name} by hand and then rerun the job.""",
                    )

            # if there is no target and no backup, the user provided invalid target table
            else:
                errors.log_and_throw(
                    to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                    log=log,
                    what_happened="Cannot find target table",
                    why_it_happened=f"Template is called for unexistent target table: {db}.{target_table}",
                    consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail.",
                    countermeasures="Provide valid target table arguments.",
                )

    def perform_safe_move_data_to_table_step(
        self,
        from_db: str,
        from_table_name: str,
        to_db: str,
        to_table_name: str,
    ):
        """
        This method creates a backup table of the target, then tries to move data from source to target.
        Source data is deleted in this process except in the situation when target data is lost.
        If moving data fails, an attemt to recover target from backup is initiated.
        :param from_db: Schema of the table that we want to rename
        :param from_table_name: Name of the table we want to rename
        :param to_db: Schema of the new table we want
        :param to_table_name: Name of the new table
        :return: None
        """
        log.debug("Create backup from target")
        backup_table_name = self.__get_backup_table_name(to_table_name)
        self.move_data_to_table(
            from_db=to_db,
            from_table_name=to_table_name,
            to_db=to_db,
            to_table_name=backup_table_name,
        )
        try:
            log.debug("Create target from tmp target")
            result = self.move_data_to_table(
                from_db=from_db,
                from_table_name=from_table_name,
                to_db=to_db,
                to_table_name=to_table_name,
            )
        except Exception as e:
            result = None
            if self.__try_recover_target_from_backup(
                to_db, to_table_name, backup_table_name
            ):
                self.drop_table(from_db, from_table_name)
                raise
            else:
                errors.log_and_throw(
                    to_be_fixed_by=errors.ResolvableBy.PLATFORM_ERROR,
                    log=log,
                    what_happened=f"""Recovering target from backup table failed. "
                        "Table {to_db}.{to_table_name} is lost!""",
                    why_it_happened=f"""Step with moving data from source to target table failed, so recovery from "
                                                "backup was initiated, but it also failed with error: {e}""",
                    consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail.",
                    countermeasures=f"""Please, try the steps bellow in the following order:\n"
                        "1. Try to rerun the data job OR\n"
                        "2. First try to recover {to_db}.{to_table_name} from"
                        "{to_db}.{backup_table_name} by manually executing:\n"
                        "CREATE TABLE {to_db}.{to_table_name} (LIKE {to_db}.{backup_table_name})\n"
                        "INSERT INTO {to_db}.{to_table_name} SELECT * FROM {to_db}.{backup_table_name}\n"
                        "Then try to rerun the data job OR\n"
                        "3. Report the issue to support team.""",
                )
        if result:
            log.debug("Target table was successfully created, and we can drop backup")
            self.drop_table(to_db, backup_table_name)

    def __try_recover_target_from_backup(
        self, db: str, target_table: str, backup_table: str
    ):
        log.debug("Try to recover target from backup")
        try:
            result = self.move_data_to_table(
                from_db=db,
                from_table_name=backup_table,
                to_db=db,
                to_table_name=target_table,
            )
        except Exception as e:
            result = None
            pass

        return result

    @staticmethod
    def __is_table_not_found_error(exception):
        return (
            isinstance(exception, TrinoUserError)
            and exception.error_name == "TABLE_NOT_FOUND"
        )

    @staticmethod
    def __get_backup_table_name(table_name):
        return "backup_" + table_name
