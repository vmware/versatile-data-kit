# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib
from abc import ABC
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from taurus.vdk.builtin_plugins.connection.managed_connection_base import (
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
    def read_properties(self, job_name: str) -> Dict:
        """
        Read properties from the backend - returns a dictionary of all properties for the given data job.
        :param job_name: the name of the job
        """
        pass

    @abstractmethod
    def write_properties(self, job_name: str, properties: Dict) -> None:
        """
        Write properties to the backend service. It overwrites all properties completely.
        :param job_name: the name of the job
        :param properties: dictionary with the new job's properties
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
    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ):
        """
        Do the actual ingestion of the payload

        :param payload: List[dict]
            The payloads to be ingested. Depending on the number of payloads to be
            processed, there might 0 or many dict objects. Each dict object is a
            separate payload.
            Note: The memory size of the list is dependent on the
            payload_size_bytes_threshold attribute.
        :param destination_table: Optional[string]
            (Optional) The name of the table, where the data should be ingested into.
            This argument is optional, and needs to be considered only when the name
            of the destination table is not included in the payload itself.
        :param target: Optional[string]
            (Optional) Used to identify where the data should be ingested into.
                Specifies a data source and its destination database.
                The values for this parameter can be in the format
                `<some-data-source_and-db-table>`, or as a URL.
                Example: http://example.com/<some-api>/<data-source_and-db-table>
            This parameter does not need to be used, in case the
            `INGEST_TARGET_DEFAULT` environment variable is set. This can be made by
            plugins, which may set default value, or it can be overwritten by users.
        :param collection_id: string
            (Optional) An identifier to indicate that data from different method
            invocations belong to same collection. Defaults to "data_job_name|OpID",
            meaning all method invocations from a data job run will belong to the
            same collection.
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
        By registering ingester objects, data enfineers would be able to use the
        same vdk setup with multiple ingester plugins, and direct where the data
        should be ingested by only specifying the `method` when calling
        send_object_for_ingestion()/send_tabular_data_for_ingestion().

        :param method: str
               Ingestion method to be associated with a plugin.
               For example:
                    method='file' -> for ingest to file plugin
                    method='http' -> for ingest over http plugin
                    method='kafka' -> for ingest to kafka endpoint plugin
        :param ingester_plugin: Callable[[], IIngesterPlugin]
               The ingester must implement the ingestion mechanism indicated by the
               method parameter.
        """
        pass
