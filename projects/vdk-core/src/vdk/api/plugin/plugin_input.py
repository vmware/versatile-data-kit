# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib
from abc import ABC
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NewType
from typing import Optional
from typing import Tuple
from typing import Union

from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)

# represents any compatible PEP249 Connection class (most of python database clients)
PEP249Connection = Any


class IPropertiesServiceClient:
    """
    Client interface for reading and writing job properties.
    Different backend services can implement it so properties can be stored in different places
    (e.g databae, inmemory, vault)
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def read_properties(self, job_name: str, team_name: str) -> Dict:
        """
        Read properties from the backend - returns a dictionary of all properties for the given data job.
        :param team_name: The name of the team the job belongs to
        :param job_name: the name of the job
        """
        pass

    @abstractmethod
    def write_properties(self, job_name: str, team_name: str, properties: Dict) -> Dict:
        """
        Write properties to the backend service. It overwrites all properties completely.
        :param team_name: The name of the team the job belongs to
        :param job_name: the name of the job
        :param properties: dictionary with the new job's properties
        :return properties: dictionary with the properties handled
        """
        pass


IPropertiesFactory = Callable[[], IPropertiesServiceClient]


class IPropertiesRegistry(ABC):
    """
    Properties registry to enable register implementation Properties service
    """

    @abstractmethod
    def set_properties_factory_method(
        self,
        properties_type: str,
        properties_factory: IPropertiesFactory,
    ) -> None:
        """
        Register properties implementation backend.
        Properties API enable keeping state and secrets of a data job.
        Default implementation is in-memory so it's strongly recommended to install vdk-properties plugin
        which provides API based properties implementation

        IPropertiesServiceClient is used as provides logic of how properties are persisted
        and is part of implementation of IProperties interface.
        See

        :param properties_type: str
                string identifying the type of properties being set.
                This enable users to configure what type of properties implemenation to use.
        :param properties_factory: Callable[[], IPropertiesServiceClient]
               method or interface that returns correctly initialized implementation of IPropertiesServiceClient interface
        """
        pass


class ITemplateRegistry:
    """
    Template registry interface for adding new data jobs as templates.

    see job_input.ITemplate for how the template will be used by Data Engineers.

    Templates functionally enables to compose data jobs within themselves.
    For example common platform team can define common data jobs as templates and use them within other data jobs.
    This interface is used by plugin developers to register new templates.

    """

    # TODO: add supported arguments so that they can be validated
    @abstractmethod
    def add_template(self, name: str, template_directory: pathlib.Path):
        """
        Register a new template.
        You usually would want to register template with job_initialize plugin hook.

        For example:

        .. code-block:: python

            @hookimpl
            def initialize_job(self, context: JobContext) -> None:
                context.templates.add_template(
                    "template_name", pathlib.Path(template_name.job_module.__file__)
                )

        :param name: The name of the template . This name will be used by users of vdk in their data jobs when invoking it
        :param template_directory: the directory which contains the implementation of the template. This is a data job which accept arguments.
        VDK will automatically run the data job internally and return result (success or not to the user.). See ITemplate for more details.
        :return:
        """
        pass


class IManagedConnectionRegistry:
    def add_open_connection_factory_method(
        self,
        dbtype: str,
        open_connection_func: Callable[
            [], Union[ManagedConnectionBase, PEP249Connection]
        ],
    ) -> None:
        """

        Register new connection factory method.
        By registering the connection it will be made available by data engineers using job_input.

        For example:

        .. code-block:: python

            @hookimpl(tryfirst=True)
            def vdk_configure(config_builder: ConfigurationBuilder) -> None:
                # Here we define what configuration settings are needed to initialize the connection
                config_builder.add(
                    key="host",  description="The host we need to connect ."
                )
                config_builder.add(
                    key="port", description="The port to connect to"
                )

            @hookimpl
            def initialize_job(context: JobContext) -> None:
                context.connections.add_open_connection_factory_method(
                    "BIG_QUERY", lambda: dbapi.connect(host=cfg.get_value('host'), post=cfg.get_value('port')
                )

        :param dbtype: the name of the database connection - e.g: redshift, impala, presto, big-query, postgres, etc.
        :param open_connection_func:
            The function must implement the code necessary to open a new connection that includes getting all configuration necessary like url, user, etc.
            The function can return either original PEP 249 (DBAPI) Connection from the python library for the given database
            or can wrap the connection into ManagedConnection by subclassing . The second method is only necessary
            if plugin does some pre / post processing and want to decorate some methods (e.g to collecto stats for each query)

        :return:
        """
        pass


class IIngesterPlugin:
    """
    Interface representing the APIs that can be used when creating Ingester
    Plugins. Plugins implement one of the methods, depending on their needs.
    If more complex processing is required, plugins can be chained
    together.

    The lifecycles of the three methods are as follows:

    ingest_payload() - plugins implementing this method are intended
                       to do actual data ingestion. Versatile Data Kit will
                       call this method when the payload that data engineers
                       have passed is ready to be ingested.

    pre_ingest_process() - plugins implementing this method do not aim at
                        ingesting the payload, rather to do some processing
                        of the payload before it is ingested.

    post_ingest_process() - plugins implementing this method aim at doing
                            some metadata processing after the payload is
                            ingested. The main use-case is telemetry data
                            collection.
                            NOTE: This method can be used only by plugins
                            that implement ingest_payload().

    Example plugin chaining workflows:

    Workflow 1
    ----------
    _____________________      _________________________      ______________
    |      Data Job     |      |    vdk-ingest-http    |      |            |
    |-------------------|      |-----------------------|      | Data Lake/ |
    |                   |      |                       |      | Warehouse/ |
    |send_object_       | ---> |   ingest_payload()    | ---> | Third-party|
    |    for_ingestion()|      |                       |      | endpoint   |
    |___________________|      |_______________________|      |____________|


    Workflow 2
    ----------                                                  ______________
                                                                |            |
    _____________________      ___________________________      | Data Lake/ |
    |      Data Job     |      |     vdk-ingest-http     |      | Warehouse/ |
    |-------------------|      |-------------------------|      | Third-party|
    |                   |      | -- ingest_payload()     | ---> | endpoint   |
    |send_object_       | ---> | |                       |      |____________|
    |    for_ingestion()|      | |                       |      ______________
    |                   |      | -->post_ingest_process()| ---> |            |
    |___________________|      |_________________________|      | Telemetry  |
                                                                | Endpoint   |
                                                                |____________|

    Workflow 3
    ----------
    _____________________   _______________   _____________   ______________
    |      Data Job     |   |vdk-validate-|   |vdk-ingest-|   |            |
    |                   |   |    data     |   |  http     |   |            |
    |-------------------|   |-------------|   |-----------|   | Data Lake/ |
    |                   |   |             |   |           |   | Warehouse/ |
    |send_object_       |-->|pre_ingest   |-->|ingest     |-->| Third-party|
    |    for_ingestion()|   |   _process()|   | _payload()|   | endpoint   |
    |                   |   |             |   |           |   |            |
    |___________________|   |_____________|   |___________|   |____________|
    """

    IngestionMetadata = NewType("IngestionMetadata", Dict)

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IngestionMetadata] = None,
    ) -> Optional[IngestionMetadata]:
        """
        Do the actual ingestion of the payload

        :param payload: List[dict]
            The payload to be ingested, split into 1 or many dictionary
            objects.
            Note: The memory size of the list is dependent on the
            payload_size_bytes_threshold attribute.
        :param destination_table: Optional[string]
            (Optional) The name of the table, where the data should be
            ingested into. This argument is optional, and needs to be
            considered only when the name of the destination table is not
            included in the payload itself.
        :param target: Optional[string]
            (Optional) Used to identify where the data should be ingested into.
                Specifies a data source and its destination database.
                The values for this parameter can be in the format
                `<some-data-source_and-db-table>`, or as a URL.
                Example:
                    http://example.com/<some-api>/<data-source_and-db-table>
            This parameter does not need to be used, in case the
            `INGEST_TARGET_DEFAULT` configuration variable is set. This can be
            made by plugins, which may set default value, or it can be
            overwritten by users.
        :param collection_id: string
            (Optional) An identifier to indicate that data from different
            method invocations belong to same collection. Defaults to
            "data_job_name|OpID", meaning all method invocations from a data
            job run will belong to the same collection.
        :param metadata: Optional[IngestionMetadata] dictionary object
            containing metadata produced and possibly used by pre-ingest,
            ingest, or post-ingest plugins.
            NOTE: A read-only parameter. Whatever modifications are done to
            this object, once returned, it is treated as a new object.

        :return: [Optional] IngestionMetadata, containing data about the
        ingestion process (information about the result from the ingestion
        operation, plugin-populated ingestion metadata, etc.). This
        metadata could be used for post-ingestion processing operations like
        sending telemetry data about the ingested payload.

        .. code-block:: python
            def ingest_payload(self,
                               payload: List[dict],
                               destination_table: Optional[str],
                               target: Optional[str] = None,
                               collection_id: Optional[str] = None,
            ) -> Optional[IngestionMetadata]:
                result = None
                metadata: IngestionMetadata = dict()
                metadata["destination_table"] = destination_table
                metadata["target"] = target

                try:
                    result = requests.post('example.com', data=payload)
                except:
                    log.info("Payload sent")

                if result:
                    metadata["http_status"] = result.status()

                return metadata

        :exception: Exceptions raised while ingesting data can either be
            handled at plugin level, or they will be automatically caught at
            the vdk-core level.
        """
        pass

    def pre_ingest_process(
        self,
        payload: List[dict],
        destination_table: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IngestionMetadata] = None,
    ) -> Tuple[List[Dict], Optional[IngestionMetadata]]:
        """
        Do some processing on the ingestion payload before passing it to the
        actual ingestion.

        For example, if we want to ensure that all values in the payload are
        string before the actual ingestion happens, we could have a plugin,
        implementing this method, and doing some payload processing:

        .. code-block:: python
            def pre_ingest_process(self,
                payload: List[dict],
                destination_table: Optional[str],
                target: Optional[str],
                collection_id: Optional[str],
                metadata: Optional[IngestionMetadata],
            ) -> Tuple[List[Dict], Optional[IngestionMetadata]]:
                # Ensure all values in the payload are strings
                processed_payload = \
                        [{k: str(v) for (k,v) in i.items()} for i in payload]

                return processed_payload, metadata

        :param payload: List[dict] the ingestion payload to be processed.
            NOTE: A read-only parameter. Whatever modifications are done to
            this object, once returned, it is treated as a new object.
        :param destination_table: Optional[string]
            (Optional) The name of the table, where the data should be
            ingested into. This argument is optional, and needs to be
            considered only when the name of the destination table is not
            included in the payload itself.
            NOTE: A read-only parameter. It is not expected to be modified and
            returned.
        :param target: Optional[string]
            (Optional) Used to identify where the data should be ingested into.
                Specifies a data source and its destination database.
                The values for this parameter can be in the format
                `<some-data-source_and-db-table>`, or as a URL.
                Example:
                      http://example.com/<some-api>/<data-source_and-db-table>
            This parameter does not need to be used, in case the
            `INGEST_TARGET_DEFAULT` configuration variable is set. This can be
            made by plugins, which may set default value, or it can be
            overwritten by users.
            NOTE: A read-only parameter. It is not expected to be modified and
            returned.
        :param collection_id: string
            (Optional) An identifier to indicate that data from different
            method invocations belong to same collection. Defaults to
            "data_job_name|OpID", meaning all method invocations from a data
            job run will belong to the same collection.
            NOTE: A read-only parameter. It is not expected to be modified and
            returned.
        :param metadata: Optional[IngestionMetadata], a dictionary object
            containing metadata produced by the pre-ingest plugin,
            and possibly used by other pre-ingest, ingest, or post-ingest
            plugins.
            NOTE: A read-only parameter. Whatever modifications are done to
            this object, once returned, it is treated as a new object.
        :return: Tuple[List[Dict], Optional[IngestionMetadata]], a tuple
            containing the processed payload objects and an
            IngestionMetadata object with ingestion metadata information.
            If no metadata is being added or processed, the metadata object
            passed to this method can be returned as is (see code block above).

        :exception: If an exception occurs during this operation, all other
            pre-processing operations and the ingestion of the payload would
            be terminated to prevent data corruption. In case the ingestion is
            expected to happen regardless if there are exceptions or not,
            then the exception handling needs to be implemented within this
            method.
        """
        pass

    def post_ingest_process(
        self,
        payload: Optional[List[dict]] = None,
        destination_table: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IngestionMetadata] = None,
        exception: Optional[Exception] = None,
    ) -> Optional[IngestionMetadata]:
        """
        Do post-ingestion processing of the ingestion payload
        or metadata from the ingestion operation.

        Example Implementation for telemetry:

        .. code-block:: python

            def post_ingest_process(
                self,
                payload: Optional[List[dict]],
                destination_table: Optional[str],
                target: Optional[str],
                collection_id: Optional[str],
                metadata: Optional[IngestionMetadata],
                exception: Optional[Exception],
            ) -> Optional[IngestionMetadata]:

                # Prepare telemetry
                telemetry = {}
                payload_sizes = [sys.getsizeof(i) for i in payload]
                telemetry['payload_size'] = sum(payload_sizes)
                telemetry['caught_ingest_exceptions'] = exceptions
                telemetry |= metadata

                # Send telemetry to wherever is needed.
                result = requests.post('example.com', data=telemetry)
                telemetry["telemetry_req_status"] = result.status_code

                return telemetry


        :param payload: Optional[List[dict]]
            The payload that has been ingested, represented as 0 or many
            dictionary objects.
            NOTE: A read-only parameter. It is not expected to be modified and
            returned.
        :param destination_table: Optional[string]
            (Optional) The name of the table, where the data should be
            ingested into. This argument is optional, and needs to be
            considered only when the name of the destination table is not
            included in the payload itself.
            NOTE: A read-only parameter. It is not expected to be modified and
            returned.
        :param target: Optional[string]
            (Optional) Used to identify where the data should be ingested into.
                Specifies a data source and its destination database.
                The values for this parameter can be in the format
                `<some-data-source_and-db-table>`, or as a URL.
                Example:
                      http://example.com/<some-api>/<data-source_and-db-table>
            This parameter does not need to be used, in case the
            `INGEST_TARGET_DEFAULT` configuration variable is set. This can be
            made by plugins, which may set default value, or it can be
            overwritten by users.
            NOTE: A read-only parameter. It is not expected to be modified and
            returned.
        :param collection_id: string
            (Optional) An identifier to indicate that data from different
            method invocations belong to same collection. Defaults to
            "data_job_name|OpID", meaning all method invocations from a data
            job run will belong to the same collection.
            NOTE: A read-only parameter. It is not expected to be modified and
            returned.
        :param metadata: Optional[IngestionMetadata]
            The metadata from the ingestion operation, that plugin developers
            have decided to process further. This metadata can be either an
            IngestionMetadata object (which is effectively a dictionary), or
            None.
            NOTE: A read-only parameter. Whatever modifications are done to
            this object, once returned, it is treated as a new object.
        :param exception: Optional[Exception]
            A caught exception (if any) encountered while ingesting data.
            NOTE: A read-only parameter. Whatever modifications are done to
            this object, once returned, it is treated as a new object.
        :return: Optional[IngestionMetadata], an IngestionMetadata object
            with information about this and possibly the previous processes (
            pre-ingestion, ingestion, post-ingestion).
        :exception: If an exception occurs during this operation, all other
            post-processing operations would be terminated to prevent data
            corruption. In case all post-process operations are expected to
            be completed regardless if there are exceptions or not, then the
            exception handling needs to be implemented within this method.
        """
        pass


class IIngesterRegistry:
    """
    Ingester Registry interface for adding different types of ingester plugins.
    """

    def add_ingester_factory_method(
        self,
        method: str,
        ingester_plugin: Callable[[], IIngesterPlugin],
    ) -> None:
        """
        Register new ingester objects.
        By registering ingester objects, data engineers would be able to use the
        same vdk setup with multiple ingester plugins, and direct where the data
        should be ingested by only specifying the `method` when calling
        send_object_for_ingestion()/send_tabular_data_for_ingestion().

        :param method: str
               Ingestion method to be associated with a plugin.
               For example:
                    method='file' -> for ingest to file plugin
                    method='http' -> for ingest over http plugin
                    method='kafka' -> for ingest to kafka endpoint plugin
               The value for the method parameter will be converted to lowercase and
               stored in this way with the aim of preventing issues where a user has
               set a variable to the correct string for a particular method, but the
               case is wrong.
        :param ingester_plugin: Callable[[], IIngesterPlugin]
               The ingester must implement the ingestion mechanism indicated by the
               method parameter.
        """
        pass
