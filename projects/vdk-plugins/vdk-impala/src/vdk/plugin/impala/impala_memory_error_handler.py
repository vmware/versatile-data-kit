# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import re

from vdk.internal.core import errors

MEMORY_LIMIT_PATTERN = r"Limit=(\d+\.\d+)\s*([KMGTP]B)"
UNITS = {"KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
MULTIPLIER = [1.2, 1.5, 2.0]


class ImpalaMemoryErrorHandler:
    def __init__(self, log=None, num_retries=5, backoff_seconds=30):
        """
        This module offers error handling for Impala Memory Errors.

        The Impala query planner projects the memory usage for every statement based on existing statistics about the
        tables involved in the statement. This statistics could be either unavailable or incorrect which leads to wrong
        memory estimates. We try to tackle this problem by gradually increasing the per executor node memory limit for
        the query and retrying it. As a last resort, we set the memory limit very high. Neither of these actions should
        cause problems for a well configured Admission Control in an Impala instance.

        For more information:
        https://impala.apache.org/docs/build/html/topics/impala_admission.html
        https://impala.apache.org/docs/build3x/html/topics/impala_mem_limit.html

        :param log: a logger object, creates a new one if one isn't passed as a parameter

        """
        if not log:
            log = logging.getLogger(__name__)
        self._log = log

    def handle_memory_error(self, exception, recovery_cursor):
        if errors.exception_matches(
            exception,
            classname_with_package="impala.error.OperationalError",
            exception_message_matcher_regex=".*Memory limit exceeded:.*",
        ) or errors.exception_matches(
            exception,
            classname_with_package="impala.error.HiveServer2Error",
            exception_message_matcher_regex=".*Memory limit exceeded:.*",
        ):
            # We are going to try to increase the memory limits and see if the query passes
            # But we won't do anything if the sql statement itself sets a memory limit
            self._log.info(
                "Query failed with memory error. We are going to increase the memory limit."
                f"Error was: {exception.__class__}: {str(exception)}"
            )
            if (
                "set memory_limit="
                in str(
                    recovery_cursor.get_managed_operation().get_operation_parameters_tuple()
                ).lower()
            ):
                self._log.info(
                    "The SQL statement you are trying to execute contains a set memory_limit option "
                    "so we are not going to handle the memory error."
                )
                return False

            # Incrementally increase the memory limit and as a last resort try to set the memory to an extreme value
            if recovery_cursor.get_retries() == 4:
                #  We won't be able to handle this error by increasing limits
                return False
            if recovery_cursor.get_retries() == 3:
                # An extreme case but let's try it as a last resort
                recovery_cursor.execute("set memory_limit=512GB;")
            else:
                self._update_memory_limit(
                    exception,
                    recovery_cursor,
                    MULTIPLIER[recovery_cursor.get_retries()],
                )
            # retry the query
            recovery_cursor.retry_operation()
            return True
        else:
            return False

    def _update_memory_limit(self, exception, recovery_cursor, multiplier):
        new_memory_limit = self._get_new_memory_limit(
            exception=exception, multiplier=multiplier
        )
        if new_memory_limit:
            self._log.info(
                f"Setting memory limit to {new_memory_limit} bytes and retrying SQL statement."
            )
            recovery_cursor.execute(f"set mem_limit={new_memory_limit};")
        else:
            self._log.warning("Unable to determine current memory limit for statement.")

    @staticmethod
    def _convert_to_bytes(value: str, unit: str):
        return int(float(value) * UNITS.get(unit, 1))

    def _get_new_memory_limit(self, exception, multiplier: float):
        memory_limit_match = re.search(MEMORY_LIMIT_PATTERN, str(exception))

        if memory_limit_match:
            memory_limit_value = memory_limit_match.group(1)
            memory_limit_unit = memory_limit_match.group(2)
            current_memory_limit = self._convert_to_bytes(
                memory_limit_value, memory_limit_unit
            )
            return int(current_memory_limit * multiplier)
        else:
            return None
