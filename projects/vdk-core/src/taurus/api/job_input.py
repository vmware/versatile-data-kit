# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import List
from typing import Optional


class IProperties:
    """
    Allows for Data Job to store state (key-value pairs) across job runs.
    Properties are solution for the following use cases

    * Keep state of application (for example last ingested row timestamp so you can continue form there on next run)
    * Keeping API keys and passwords necessary to connect to different systems
    * Keeping custom configuration of a data job.

    Data Job properties are also used for parameter substitution in queries, see execute_query docstring.
    """

    @abstractmethod
    def get_property(self, name: str, default_value: Any = None) -> str:
        pass

    @abstractmethod
    def get_all_properties(self) -> dict:
        pass

    @abstractmethod
    def set_all_properties(self, properties: dict):
        pass


class IJobArguments:
    """
    Allows for users to pass arguments to data job run.

    Data Job arguments are also used for parameter substitution in queries, see execute_query docstring.
    """

    @abstractmethod
    def get_arguments(self) -> dict:
        """
        Returns arguments are passed when running data job. Arguments present dictionary key value pairs.
        The arguments are passed to each step.
        """
        pass


class IManagedConnection:
    """
    Takes care of managing raw database connections.
    It provides features improved error handling, lineage gathering, smart re-tries.
    And more that can be easily customized and extended by VDK plugins.
    """

    @abstractmethod
    def execute_query(self, query_as_utf8_string) -> List[List]:
        """
        Executes the provided query and returns results from PEP 249 Cursor.fetchall() method, see:
            https://www.python.org/dev/peps/pep-0249/#fetchall

        Query can contain parameters in format -> {query_parameter}. Parameters in the query will
        be automatically substituted if they exist in Data Job properties and arguments as keys.

        Note:
            Parameters are case sensitive.
            If a query parameter is not present in Data Job properties it will not be replaced in the query
            and most likely result in query failure.

        Example usage:
            job_input.set_all_properties({'target_table': 'history.people','etl_run_date_column': 'pa__arrival_ts'})
            query_result = job_input.execute_query("SELECT * FROM {target_table} WHERE {etl_run_date_column} > now() - interval 2 hours")

        """
        pass

    @abstractmethod
    def get_managed_connection(self):
        """
        Returns the currently initialized PEP249 connection.
        In this case to execute query you need to open and close cursor yourself.
        It's generally easier to use #execute_query method above,
        Use this method if you need to pass connection to 3th party library (sqlAlchemy or pandas)
        """


class IIngester:
    """
    Methods in this interface are suitable for ingesting new data into remote data stores.

    The Ingester client provides an easy to use and thread-safe APIs to collect and transfer data to any destination.
    It offers a simple, best effort solution for serializing, packaging, and sending data.

    send_*_for_ingestion provide a way to send data easily form database cursor, API response,
     or any other python iterable collection.

    The client can be configured via configuration overrides, or left on default settings.

    The methods are asynchronous, and data being sent is done in a background threads.
    This library allows buffering of data on the client before sending it.
    You can also configure the frequency at which data is sent .
    You can configure the parallelism in which the data is sent enabling very high throughput of sending data.

    Upon job completion, the job may block until all buffers are flushed and data is sent.
    if there's an error during sending data, the data job will fail upon completion with a corresponding error.

    Destinations method can be installed using plugins
    (for example plugins for sending over http, or over kafka, or over GCloud Pub/Sub, etc.)

    """

    @abstractmethod
    def send_object_for_ingestion(
        self,
        payload: dict,
        destination_table: Optional[str],
        method: Optional[str],
        target: Optional[str],
        collection_id: Optional[str] = None,
    ):
        """
        Sends a Python object, asynchronously, for ingestion.

        Arguments:
            payload: dict
                The passed object will be translated to a row in destination table.
                Keys of the object are translated to columns in the table and values will populate a single row.

                Note:
                    This method hides technical complexities around @type and @id
                    described in the specification, still you have the freedom to
                    specify @type and @id.

                    object size should be less than 10MB.
                Example:
                    object = {
                        "address":"1 Main St. Cambridge MA",
                        "name":"John Doe"
                    }

                    Will produce the following DB row:
                    _____________________________________________
                    |address                |name          |... |
                    |_______________________|______________|____|
                    |1 Main St. Cambridge MA|John Doe      |... |
                    |_______________________|______________|____|

            destination_table: Optional[str]
                The name of the table, where the data should be ingested into.
                This parameter does not need to be passed, in case the table is
                included in the payload itself.

            method: Optional[str]
                Indicates the ingestion method to be used. Example:
                    method="file" -> ingest to file
                    method="http" -> ingest using HTTP POST requests
                    method="kafka" -> ingest to kafka endpoint
                This parameter does not need to be passed, as ingestion plugins set
                a default value for it. In case multiple ingestion plugins are used,
                an `INGEST_METHOD_DEFAULT` environment variable can be set that would
                specify which plugin is to be used by default for ingestion.

            target: Optional[str]
                target identifies where the data should be ingested into. Specifies
                a data source and its destination database.

                The values for this parameter can be in the format
                `<some-data-source_and-db-table>`, or as a URL.
                Example: http://example.com/<some-api>/<data-source_and-db-table>

                The `__STAGING/__PRODUCTION` can be added at the end of the target if
                separation of dev/test from production data is required.

                This parameter does not need to be used, in case the
                `INGEST_TARGET_DEFAULT` environment variable is set. This can be
                made by plugins, which may set default value, or it can be
                overwritten by users.

            collection_id: Optional[str]
                Optional. An identifier to indicate that data from different method
                invocations belong to same collection. Defaults to
                "data_job_name|OpID", meaning all method invocations from a data job
                run will belong to the same collection.


        Sample usage:
            response = requests.get("https://jsonplaceholder.typicode.com/users/1") # call some REST API
            job_input.send_object_for_ingestion(response.json(),
                                                "my_destination_table",
                                                method="file"
                                                target="some-target")
        """
        pass

    @abstractmethod
    def send_tabular_data_for_ingestion(
        self,
        rows: iter,
        column_names: list,
        destination_table: Optional[str],
        method: Optional[str],
        target: Optional[str],
        collection_id: Optional[str] = None,
    ):
        """
        Sends tabular data, asynchronously, for ingestion.

        Arguments:
            rows: one of the following: PEP249 Cursor object, Iterable 2 dimensional
                    structure, A representation of a
                    two-dimensional array that allows iteration over rows.
                    Can be a list of lists, iterator that returns next row
                    ("row" = list or tuple of values),
                    PEP249 cursor object with successfully executed SELECT statement,
                    etc. E.g.:
                    [
                        [row0column0, row0column1]
                        [row1column0, row1column1]
                    ]

            column_names: list
                the column names of the data in the same order as the values in data
                provided in th rows parameter.
                col[0] - corresponds to row0column0,row1column0,
                col[1] to row0column1, row1column1.


            destination_table: Optional[str]
                The name of the table, where the data should be ingested into.
                This parameter does not need to be passed, in case the table is
                included in the payload itself.

            method: Optional[str]
                Indicates the ingestion method to be used. Example:
                    method="file" -> ingest to file
                    method="http" -> ingest using HTTP POST requests
                    method="kafka" -> ingest to kafka endpoint
                This parameter does not need to be passed. In case multiple ingestion plugins are used,
                an `VDK_INGEST_METHOD_DEFAULT` environment variable can be set that would
                specify which plugin is to be used by default for ingestion.

                Different methods can be added through Plugins.
                See plugin_input for how to develop a new plugin with new ingest method.

            target: Optional[str]
                target identifies where the data should be ingested into. Specifies
                a data source and its destination database.

                The values for this parameter can be in the format
                `<some-data-source_and-db-table>`, or as a URL.
                Example: http://example.com/<some-api>/<data-source_and-db-table>

                This parameter does not need to be used. In case the
                `VDK_INGEST_TARGET_DEFAULT` environment variable is set it will be used.
                 If not plugins  may set default value.

            collection_id: Optional[str]
                Optional. An identifier to indicate that data from different method
                invocations belong to same collection. Defaults to
                "data_job_name|OpID", meaning all method invocations from a data job
                run will belong to the same collection.

        Sample usage:
            tabular_data = [[ "row1column1", 11], ["row2column1", 21]]
            job_input.send_tabular_data_for_ingestion(tabular_data,
                                                      "my_destination_table",
                                                      method="file"
                                                      target="my-target")

            db_connection = initialize_db_connection()
            cursor = db_connection.cursor()
            cursor.execute("SELECT * FROM table")
            job_input.send_tabular_data_for_ingestion(cursor,
                                          [column_info[0] for column_info in cursor.description],
                                          "my_destination_table",
                                          method="file",
                                          target="my-target")
            cursor.close()
        """
        pass


class ITemplate:
    """
    Templates interface enables to package a whole data job and execute it as single operation.
    """

    from taurus.vdk.builtin_plugins.run.execution_results import ExecutionResult

    @abstractmethod
    def execute_template(
        self, template_name: str, template_args: dict
    ) -> ExecutionResult:
        """
        Execute a data job template.

        Templates are pieces of reusable code, which is common to use cases of different customers of VDK.
        Templates are executed in the context of a Data Job..
        They provide an easy solution to common tasks of loading data to a data warehouse or ingesting data in a common way.
        For example there are templaets for:
        * Slowly Changing Dimension Type 1 strategy overwrites the data in target table with the data defined in the source
        * Slowly Changing Dimension Type 2 accumulates updates from the data source as versioned records in the target table

        There could be many types of templates. Any data job can be made into a template - since at its core template is reusable data job.

        You can see the full list of available templates and instructions on their usage here: TODO

        Arguments:

            template_name: str
                Name of data loading template

            template_args: dict
                Arguments to be passed to the template
        """
        pass


class IJobInput(IProperties, IManagedConnection, IIngester, ITemplate, IJobArguments):
    @abstractmethod
    def get_name(self) -> str:
        """
        :return: the name of the currently executing job (can be base data job or template job)
        """

    @abstractmethod
    def get_job_directory(self) -> pathlib.Path:
        """
        :return: the code location of the currently executing job (can be base data job or template job)
        """

    @abstractmethod
    def get_execution_properties(self) -> dict:
        """
        :return: a dictionary with execution-related properties for the current job execution. Example properties:
            pa__execution_id: str - Identifier of the execution of this job. (equal to OpID when this job is the first job
                from the workflow of jobs that are being executed)
            pa__job_start_unixtime: str - the start time of this job in seconds since epoch (an integer number).
            pa__job_start_ts_expr: str - a Impala-valid SQL expression that returns a TIMESTAMP that represents job start time.
            pa__op_id: str - the Operation ID - identifies the trigger that initiated this job. It is possible to have N jobs
                with same OpID (if Job1 started Job2 then Job1.opId = Job2.opId)
        Usage:
            job_input.get_execution_properties()['pa__job_start_unixtime'] #returns e.g. 1560179839
            Those properties can also be used as arguments in SQL. E.g. a .sql file in your job may contain this SELECT:
                SELECT id, {pa__job_start_ts_expr} FROM mytable
        """
        pass
