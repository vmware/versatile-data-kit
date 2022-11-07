# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import re
import time

from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.core import errors


class ImpalaErrorHandler:
    def __init__(self, log=None, num_retries=5):
        """
        This module offers error handling and error recovery for an Impala connection.

        :param log: a logger object, creates a new one if one isn't passed as a parameter
        :param num_retries: number of times a query will be re-tried
        """
        if not log:
            log = logging.getLogger(__name__)
        self._log = log

        self._num_retries = num_retries

    def handle_error(
        self, caught_exception: Exception, recovery_cursor: RecoveryCursor
    ) -> bool:
        """
        Handles an exception/error thrown by Impala.
        It examines the error and depending on which case it matches it will
        take measures to fix the problem and/or re-try the query.

        For example, let's consider a "File Not Found" error.
        Queries can fail when they are querying for tables which have been recently compacted.
        In such a case, the following steps are undertaken:
            1. Examine exception to detect if this is the case;
            2. If it is, then issue a refresh for the table whose files could not be found;
            3. Re-try the query.

        :param caught_exception: the caught Impala exception
        :param recovery_cursor: cursor that can be used to execute recovery queries and query retries against Impala
        :return: true if and only if the exception was handled successfully and the query passed has succeeded.
                Otherwise return false - the caught_exception was not handled.
                This method will raise an exception in the following scenarios and assuming handling of the error
                produced another exception:
                 1. Exceptions are of the same type but have different args.
                 2. Exceptions are different types.
                Moreover, the root cause stack trace will appear in the error message if an exception is raised.
                Otherwise stacktrace gets changed and becomes confusing.
        """
        if self._handle_should_not_retry_error(caught_exception):
            return False

        if self._is_pool_error(caught_exception):
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=self._log,
                what_happened="An Impala Pool Error occured: " + str(caught_exception),
                why_it_happened="Review the contents of the exception.",
                consequences="The queries will not be executed.",
                countermeasures=(
                    "Optimise the executed queries. Alternatively, make sure that "
                    "the data job is not running too many queries in parallel."
                ),
            )

        is_handled = False
        # try to handle multiple failed to open file errors in one query for different tables
        current_exception = caught_exception
        while recovery_cursor.get_retries() < self._num_retries:
            self._log.info(
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
        # The call to the _handle_impala_network_error() method below needs to stay at the end, as
        # it catches all OperationalError cases not caught in the preceding method calls.
        return (
            self._handle_hdfs_failed_to_open_file_error(exception, recovery_cursor)
            or self._handle_metadata_exception_with_backoff(exception, recovery_cursor)
            or self._handle_metadata_exception_with_invalidate_and_backoff(
                exception, recovery_cursor
            )
            or self._handle_metadata_exception_with_invalidate_and_retry(
                exception, recovery_cursor
            )
            or self._handle_impala_network_error(exception, recovery_cursor)
        )

    def _handle_should_not_retry_error(self, exception) -> bool:
        if errors.exception_matches(
            exception,
            classname_with_package="impala.error.OperationalError",
            exception_message_matcher_regex=".*expired due to execution time limit.*",
        ):
            self._log.info(
                "Execution of query exceeded impala time limit. "
                "This is most likely because the query is resource heavy and needs optimisation. "
                "The query would not be retried, in order to avoid increasing the load on the database."
            )
            return True

        return False

    def _handle_hdfs_failed_to_open_file_error(
        self, exception, recovery_cursor
    ) -> bool:
        if errors.exception_matches(
            exception, "impala.error.OperationalError", ".*Failed to open HDFS.*"
        ) or errors.exception_matches(
            exception, "impala.error.HiveServer2Error", ".*Failed to open HDFS.*"
        ):
            regex = ".*/user/hive/warehouse/([^/]*).db/([^/]*)"
            matcher = re.compile(pattern=regex, flags=re.DOTALL)
            results = matcher.search(str(exception).strip())
            self._log.info(
                "Detected query failing with Failed to find file error. WIll try to autorecover."
            )
            if results and len(results.groups()) == 2:
                database = results.group(1)
                table = results.group(2)
                self._log.info(
                    "Query failed with with Failed to find file error. "
                    "This is most likely due to delay metadata sync from compaction. "
                    f"We are issuing refresh statement for the offending table: {database}.{table}"
                    " and retrying the query"
                    f"Error was: {exception.__class__}: {str(exception)}"
                )
                # Try refreshing the table metadata several times,
                # and if the issue is not fixed invalidate the metadata.
                if recovery_cursor.get_retries() > 3:
                    recovery_cursor.execute(
                        "invalidate metadata `" + database + "`.`" + table + "`"
                    )
                else:
                    recovery_cursor.execute(
                        "refresh `" + database + "`.`" + table + "`"
                    )
                    time.sleep(
                        2 ** recovery_cursor.get_retries() * 30
                    )  # exponential backoff 30s, 60s, 2m, 4m, 8m
                recovery_cursor.retry_operation()
                return True
            else:
                self._log.info(
                    f"Cannot auto-recover as it cannot detect table name in error: {exception}"
                )
        return False

    def _handle_impala_network_error(self, exception, recovery_cursor) -> bool:
        if (
            errors.exception_matches(
                exception,
                classname_with_package="impala.error.OperationalError",
                exception_message_matcher_regex=".*.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="impala.error.HiveServer2Error",
                exception_message_matcher_regex=".*Connection refused.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="impala.error.HiveServer2Error",
                exception_message_matcher_regex=".*Failed after retrying 3 times.*",
            )
        ):
            self._log.info(
                "Query failed with network error. This is most likely a recoverable error. "
                "We are retrying the query. "
                f"Error was: {exception.__class__}: {str(exception)}"
            )
            # wait a little before retrying the query, giving time for the network to recover
            if recovery_cursor.get_retries() > 0:
                time.sleep(
                    2 ** recovery_cursor.get_retries() * 30
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
                classname_with_package="impala.error.HiveServer2Error",
                exception_message_matcher_regex=".*AnalysisException: Could not resolve column/field reference.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="impala.error.HiveServer2Error",
                exception_message_matcher_regex=".*OutOfMemoryError: null.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="impala.error.OperationalError",
                exception_message_matcher_regex=".*ImpalaRuntimeException: Error making 'alter_table' RPC to Hive.*",
            )
            or errors.exception_matches(
                exception,
                classname_with_package="impala.error.OperationalError",
                exception_message_matcher_regex=".*ImpalaRuntimeException: Error making 'updateTableColumnStatistics'.*",
            )
        ):

            sleep_seconds = 2 ** recovery_cursor.get_retries() * 30
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

    def _handle_metadata_exception_with_invalidate_and_backoff(
        self, exception, recovery_cursor
    ) -> bool:
        pattern_for_the_table_name = None

        if errors.exception_matches(
            exception,
            classname_with_package="impala.error.OperationalError",
            exception_message_matcher_regex=".*TableLoadingException: Error loading metadata for table.*",
        ):
            pattern_for_the_table_name = (
                ".*TableLoadingException: Error loading metadata for table: (\\S+).*"
            )

        if errors.exception_matches(
            exception,
            classname_with_package="impala.error.HiveServer2Error",
            exception_message_matcher_regex=".*TableLoadingException: Error loading metadata for table.*",
        ):
            pattern_for_the_table_name = (
                ".*TableLoadingException: Error loading metadata for table: (\\S+).*"
            )

        if errors.exception_matches(
            exception,
            classname_with_package="impala.error.HiveServer2Error",
            exception_message_matcher_regex=".*LocalCatalogException: Could not load table.*",
        ):
            pattern_for_the_table_name = (
                ".*LocalCatalogException: Could not load table (\\S+) from metastore.*"
            )

        if errors.exception_matches(
            exception,
            classname_with_package="impala.error.HiveServer2Error",
            exception_message_matcher_regex=".*AnalysisException: Could not resolve table reference.*",
        ):
            pattern_for_the_table_name = (
                ".*AnalysisException: Could not resolve table reference: '(\\S+)'.*"
            )

        if (
            pattern_for_the_table_name
        ):  # then one of the exceptions matched and we can handle with invalidate
            sleep_seconds = 2 ** recovery_cursor.get_retries() * 30
            self._log.info(
                f"Query failed with: {exception.__class__} : {str(exception)}"
                f"Will sleep for {sleep_seconds} seconds, will issue invalidate metadata on the table and try the query again."
            )

            # Get the fully qualified table name from the exception message.
            matcher = re.compile(pattern=pattern_for_the_table_name)
            results = matcher.search(str(exception).strip())
            if results and len(results.groups()) == 1:
                fully_qualified_table_name = results.group(1)
                # invalidate the metadata for the missing table
                recovery_cursor.execute(
                    f"invalidate metadata {fully_qualified_table_name}"
                )
                # wait a little before retrying the query, relaxing the stress on the metastore service
                self._log.info(
                    f"Sleeping for {sleep_seconds} seconds before retrying the query ..."
                )
                time.sleep(sleep_seconds)  # exponential backoff 30s, 60s, 2m, 4m, 8m
                # retry the query
                recovery_cursor.retry_operation()
                return True
        return False

    # The method is meant to handle only failed queries, whose metadata needs to be invalidated, and that should
    # be retried only once to avoid overloading the database.
    def _handle_metadata_exception_with_invalidate_and_retry(
        self, exception, recovery_cursor
    ) -> bool:
        def check_exception_and_get_pattern_for_table_name(exception_to_match):
            pattern = None
            if errors.exception_matches(
                exception_to_match,
                classname_with_package="impala.error.HiveServer2Error",
                exception_message_matcher_regex=".*AnalysisException: Table does not exist:.*",
            ):
                pattern = ".*AnalysisException: Table does not exist: (\\S+)"
            if errors.exception_matches(
                exception_to_match,
                classname_with_package="impala.error.HiveServer2Error",
                exception_message_matcher_regex=".*AlreadyExistsException: Table.*",
            ):
                pattern = ".*AlreadyExistsException: Table (\\S+).*"
            if errors.exception_matches(
                exception_to_match,
                classname_with_package="impala.error.HiveServer2Error",
                exception_message_matcher_regex=".*LocalCatalogException: Could not load.*",
            ):
                pattern = ".*LocalCatalogException: Could not load (\\S+).*"
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
                f"Will sleep for {sleep_seconds} seconds, will issue invalidate"
                " metadata on the table and try the query again."
            )

            # invalidate the metadata for the table. This is necessary in case the metadata for the table
            # has not been propagated before the query is executed again.
            recovery_cursor.execute(f"invalidate metadata {detected_table}")
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
                        f"We tried to invalidate metadata for {detected_table} "
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
        Check for impala pool errors.
        """
        return errors.exception_matches(
            exception,
            classname_with_package=".*OperationalError.*",
            exception_message_matcher_regex=".*queue full.*",
        ) or errors.exception_matches(
            exception,
            classname_with_package=".*OperationalError.*",
            exception_message_matcher_regex=".*admission for timeout ms in pool.*",
        )
