# Copyright 2024-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import re
import time

from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.core import errors
from vdk.internal.core.errors import UserCodeError

MEMORY_LIMIT_PATTERN = r"Limit=(\d+\.\d+)\s*([KMGTP]B)"


class TrinoErrorHandler:
    def __init__(self, log=None, num_retries=5, backoff_seconds=30):
        """
        This module offers error handling and error recovery for an Trino connection.

        :param log: a logger object, creates a new one if one isn't passed as a parameter
        :param num_retries: number of times a query will be re-tried
        """
        if not log:
            log = logging.getLogger(__name__)
        self._log = log

        self._num_retries = num_retries
        self._backoff_seconds = backoff_seconds

    def handle_error(
        self, caught_exception: Exception, recovery_cursor: RecoveryCursor
    ) -> bool:
        """
        Handles an exception/error thrown by Trino.
        It examines the error and depending on which case it matches it will
        take measures to fix the problem and/or re-try the query.

        For example, let's consider a "File Not Found" error.
        Queries can fail when they are querying for tables which have been recently compacted.
        In such a case, the following steps are undertaken:
            1. Examine exception to detect if this is the case;
            2. If it is, then issue a refresh for the table whose files could not be found;
            3. Re-try the query.

        :param caught_exception: the caught Trino exception
        :param recovery_cursor: cursor that can be used to execute recovery queries and query retries against Trino
        :return: true if and only if the exception was handled successfully and the query passed has succeeded.
                Otherwise, return false - the caught_exception was not handled.
                This method will raise an exception in the following scenarios and assuming handling of the error
                produced another exception:
                 1. Exceptions are of the same type but have different args.
                 2. Exceptions are different types.
                Moreover, the root cause stack trace will appear in the error message if an exception is raised.
                Otherwise, stacktrace gets changed and becomes confusing.
        """
        if self._handle_should_not_retry_error(caught_exception):
            return False

        if self._is_pool_error(caught_exception):
            errors.report_and_throw(
                UserCodeError(
                    "An Trino Pool Error occurred: " + str(caught_exception),
                    "Review the contents of the exception.",
                    "The queries will not be executed.",
                    "Optimise the executed queries. Alternatively, make sure that "
                    "the data job is not running too many queries in parallel.",
                )
            )

        is_handled = False
        # try to handle multiple failed to open file errors in one query for different tables
        current_exception = caught_exception
        while recovery_cursor.get_retries() < self._num_retries:
            self._log.debug(
                f"Try ({(recovery_cursor.get_retries() + 1)} of {self._num_retries}) "
                f"to handle exception {current_exception}"
            )
            try:
                is_handled = self._handle_exception(current_exception, recovery_cursor)
                break
            except Exception as new_exception:
                self._log.warning(f"Failed to handle exception due to: {new_exception}")
                current_exception = new_exception
        # Throw the latest exception only if different from the initial exception.
        if not is_handled and (
            type(current_exception) is not type(caught_exception)
            or current_exception.args != caught_exception.args
        ):
            self._log.warning(
                "Query failed with an exception. We tried handling and resolving the original error: "
                + f"({(type(caught_exception))}) by retrying the query "
                f"({(recovery_cursor.get_retries())}) times. "
                + "Another exception occurred during handling of the above mentioned error. "
                + "Throwing the exception which occurred during the latest retry of the original error. "
                + "For more information on both errors check the stack trace bellow: "
            )
            raise current_exception
        return is_handled

    def _handle_exception(self, exception, recovery_cursor) -> bool:
        return (
            self._handle_hdfs_failed_to_open_file_error(exception, recovery_cursor)
            or self._handle_metadata_exception_with_backoff(exception, recovery_cursor)
            or self._handle_metadata_exception_with_refresh_and_retry(
                exception, recovery_cursor
            )
            or self._handle_trino_network_error(exception, recovery_cursor)
        )

    def _handle_should_not_retry_error(self, exception) -> bool:
        if errors.exception_matches(
            exception,
            classname_with_package="trino.exceptions.TrinoException",
            exception_message_matcher_regex="^TIMEOUT.*",
        ) or errors.exception_matches(
            exception,
            classname_with_package="trino.exceptions.TrinoException",
            exception_message_matcher_regex="^EXCEEDED_TIME_LIMIT.*",
        ):
            self._log.info(
                "Execution of query exceeded trino time limit. "
                "This is most likely because the query is resource heavy and needs optimisation. "
            )
            return True

        return False

    def _handle_hdfs_failed_to_open_file_error(
        self, exception, recovery_cursor
    ) -> bool:
        if errors.exception_matches(
            exception, "trino.exceptions.TrinoException", ".*Failed to open HDFS file.*"
        ):
            regex = ".*/user/hive/warehouse/([^/]*).db/([^/]*)"
            matcher = re.compile(pattern=regex, flags=re.DOTALL)
            results = matcher.search(str(exception).strip())
            self._log.debug(
                "Detected query failing with Failed to find file error. WIll try to auto recover."
            )
            if results and len(results.groups()) == 2:
                database = results.group(1)
                table = results.group(2)
                self._log.info(
                    "Query failed with Failed to find file error. "
                    "This is most likely due to delay metadata sync from compaction. "
                    f"We are issuing refresh statement for the offending table: {database}.{table}"
                    " and retrying the query"
                    f"Error was: {exception.__class__}: {str(exception)}"
                )
                # Try refreshing the table metadata several times,
                # and if the issue is not fixed invalidate the metadata.
                try:
                    if recovery_cursor.get_retries() > 3:
                        recovery_cursor.execute(
                            "invalidate metadata " + database + "." + table + ""
                        )
                    else:
                        recovery_cursor.execute(
                            "refresh " + database + "." + table + ""
                        )
                        time.sleep(
                            2 ** recovery_cursor.get_retries() * self._backoff_seconds
                        )  # exponential backoff 30s, 60s, 2m, 4m, 8m
                except Exception as e:
                    self._log.info(
                        f"Refresh/Invalidate metadata operation failed with error: {e}"
                    )
                    time.sleep(
                        2 ** recovery_cursor.get_retries() * self._backoff_seconds
                    )  # exponential backoff 30s, 60s, 2m, 4m, 8m
                recovery_cursor.retry_operation()
                return True
            else:
                self._log.info(
                    f"Cannot auto-recover as it cannot detect table name in error: {exception}"
                )
        return False

    def _handle_trino_network_error(self, exception, recovery_cursor) -> bool:
        if errors.exception_matches(
            exception,
            classname_with_package="trino.exceptions.TrinoException",
            exception_message_matcher_regex=".*Error communicating with the data source.*",
        ) or errors.exception_matches(
            exception,
            classname_with_package="trino.exceptions.TrinoException",
            exception_message_matcher_regex=".*Connection refused.*",
        ):
            self._log.info(
                "Query failed with network error. This is most likely a recoverable error. "
                "We are retrying the query. "
                f"Error was: {exception.__class__}: {str(exception)}"
            )
            # wait a little before retrying the query, giving time for the network to recover
            if recovery_cursor.get_retries() > 0:
                time.sleep(
                    2 ** recovery_cursor.get_retries() * self._backoff_seconds
                )  # exponential backoff 60s, 2m, 4m, 8m
            # retry the query
            recovery_cursor.retry_operation()
            return True
        else:
            return False

    def _handle_metadata_exception_with_backoff(
        self, exception, recovery_cursor
    ) -> bool:
        if (
            errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*TABLE_HAS_NO_COLUMNS.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*INVALID_COLUMN_PROPERTY.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*COLUMN_NOT_FOUND.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*COLUMN_ALREADY_EXISTS.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*DUPLICATE_COLUMN_NAME.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*EXCEEDED_LOCAL_MEMORY_LIMIT.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*CLUSTER_OUT_OF_MEMORY.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*EXCEEDED_GLOBAL_MEMORY_LIMIT.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*EXCEEDED_FUNCTION_MEMORY_LIMIT.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*Error making 'alter_table' RPC to Hive.*",
            )
        ):
            sleep_seconds = 2 ** recovery_cursor.get_retries() * self._backoff_seconds
            self._log.info(
                f"Query failed with: {exception.__class__} : {str(exception)}"
                f"Will sleep for {sleep_seconds} seconds and try the query again."
            )
            # wait a little before retrying the query, giving time for the metadata to sync
            time.sleep(sleep_seconds)  # exponential backoff 30s, 60s, 2m, 4m, 8m
            # retry the query
            recovery_cursor.retry_operation()
            return True
        else:
            return False

    # The method is meant to handle only failed queries, whose metadata needs to be refreshed, and that should
    # be retried only once to avoid overloading the database.
    def _handle_metadata_exception_with_refresh_and_retry(
        self, exception, recovery_cursor
    ) -> bool:
        def check_exception_and_get_pattern_for_table_name(exception_to_match):
            pattern = None
            if errors.exception_matches(
                exception_to_match,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*TABLE_NOT_FOUND: Table (\\S+) not found.*",
            ):
                pattern = ".*TABLE_NOT_FOUND: Table (\\S+) not found"
            if errors.exception_matches(
                exception_to_match,
                classname_with_package="trino.exceptions.TrinoException",
                exception_message_matcher_regex=".*ALREADY_EXISTS: Table (\\S+) already exists.*",
            ):
                pattern = ".*ALREADY_EXISTS: Table (\\S+) already exists.*"
            return pattern

        def get_fully_qualified_table_name(exception_to_match: Exception):
            pattern_for_the_table_name = check_exception_and_get_pattern_for_table_name(
                exception_to_match
            )
            if pattern_for_the_table_name:
                # Get the fully qualified table name from the exception message.
                matcher = re.compile(pattern=pattern_for_the_table_name)
                results = matcher.search(str(exception_to_match).strip())
                if results and len(results.groups()) == 1:
                    fully_qualified_table_name = results.group(1)

                    # Data Mart name may not be available from the exception message, so we need to extract it
                    # from the query.
                    if "." not in fully_qualified_table_name:
                        try:
                            schema_match = re.search(
                                r"create (?:table|view)\b\s`?(\w+)`?\.{}".format(
                                    fully_qualified_table_name
                                ),
                                recovery_cursor.get_managed_operation().get_operation(),
                                re.IGNORECASE,
                            ).group(1)
                            fully_qualified_table_name = (
                                f"{schema_match}.{fully_qualified_table_name}"
                            )
                        except AttributeError:
                            self._log.info(
                                "Could not retrieve table name %s from provided query."
                                % fully_qualified_table_name
                            )

                            return None

                    return fully_qualified_table_name
                return None
            return None

        detected_table = get_fully_qualified_table_name(exception)
        if detected_table:
            # then one of the exceptions matched and we can handle with invalidate
            sleep_seconds = 10
            self._log.info(
                f"Query failed with: {exception.__class__} : {str(exception)}"
                f"Will sleep for {sleep_seconds} seconds, will issue refresh"
                " metadata on the table and try the query again."
            )

            # Refresh the metadata for the table. This is necessary in case the metadata for the table
            # has not been propagated before the query is executed again.
            try:
                recovery_cursor.execute(f"REFRESH {detected_table}")
            except Exception as e:
                self._log.info(f"Refresh metadata operation failed with error: {e}")
            # wait a little before retrying the query, relaxing the stress on the metastore service
            self._log.info(
                f"Sleeping for {sleep_seconds} seconds before retrying the query ..."
            )
            time.sleep(sleep_seconds)  # sleep for 20s
            # retry the query
            try:
                recovery_cursor.retry_operation()
            except Exception as new_exception:
                new_detected_table = get_fully_qualified_table_name(new_exception)
                if new_detected_table == detected_table:
                    self._log.info(
                        f"We tried to refresh metadata for {detected_table} "
                        f"and retry query but it did not seem to work."
                        "We give up and will not try again"
                    )
                    return False
                # new exception is different so we re-raise so it can be handled again.
                raise

            return True
        return False

    @staticmethod
    def _is_pool_error(exception: Exception) -> bool:
        """
        Check for trino pool errors.
        """
        return errors.exception_matches(
            exception,
            classname_with_package=".*trino.exceptions.TrinoException.*",
            exception_message_matcher_regex=".*QUERY_QUEUE_FULL.*",
        )
