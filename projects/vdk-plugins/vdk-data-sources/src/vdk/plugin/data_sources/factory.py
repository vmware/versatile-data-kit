# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import Collection
from typing import Dict
from typing import List
from typing import Type

from vdk.api.job_input import IProperties
from vdk.plugin.data_sources import config
from vdk.plugin.data_sources.data_source import IDataSource
from vdk.plugin.data_sources.data_source import (
    IDataSourceConfiguration,
)
from vdk.plugin.data_sources.state import IDataSourceState


@dataclass
class DataSourceRegistryItem:
    """
    A registry item for Data Sources.

    :param name: The name identifier for the data source
    :param instance_class: The data source class that implements `IDataSource`
    :param config_class: The configuration class that implements `IDataSourceConfiguration`
    """

    name: str
    instance_class: Type[IDataSource]
    config_class: Type[IDataSourceConfiguration]


class DataSourceNotFoundException(Exception):
    def __int__(self, data_source_name: str, existing_data_source_names: List[str]):
        super().__init__(
            f"Data source with name {data_source_name} does not exists. "
            f"Existing data sources are {existing_data_source_names}"
        )

    pass


class IPropertiesDataSourceState(IDataSourceState):
    """
    A stateful data source implementation using `IProperties` to manage state.
    """

    PREFIX = ".IDataSource"

    def __int__(self, data_source_name: str, properties: IProperties):
        self.__properties = properties
        self.__data_source_name = data_source_name

    def read(self) -> Dict[str, Any]:
        states: Dict = self.__properties.get_property(self.PREFIX, {})
        return states.get(self.__data_source_name, {})

    def write(self, state: Dict[str, Any]):
        all_properties = self.__properties.get_all_properties()
        all_properties.setdefault(self.PREFIX, {})[self.__data_source_name] = state
        self.__properties.set_all_properties(all_properties)


class IDataSourceFactory:
    @abstractmethod
    def register_data_source(
        self,
        name: str,
        data_source_class: Type[IDataSource],
        data_source_config_class: Type[IDataSourceConfiguration],
    ):
        """
        Register a data source and its associated configuration class.

        :param name: The name identifier for the data source
        :param data_source_class: The data source class that implements `IDataSource`
        :param data_source_config_class: The configuration class that implements `IDataSourceConfiguration`
        """

    @abstractmethod
    def list(self) -> Collection[DataSourceRegistryItem]:
        """
        List all registered data sources.

        :return: A collection of registered data sources
        """

    @abstractmethod
    def create_data_source(self, name: str) -> IDataSource:
        """
        Create an instance of a registered data source.

        :param name: The name identifier for the data source
        :return: An instance of the data source
        """


class SingletonDataSourceFactory(IDataSourceFactory):
    """
    Singleton factory class to create and manage Data Source instances.
    The factory holds a registry of Data Source classes and their associated configuration classes.
    """

    _instance = None

    def __new__(cls):
        """
        Implement the Singleton pattern by creating a single instance or returning the existing one.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__data_source_registry = {}
        return cls._instance

    def register_data_source(
        self,
        name: str,
        data_source_class: Type[IDataSource],
        data_source_config_class: Type[IDataSourceConfiguration],
    ):
        self.__data_source_registry[name] = DataSourceRegistryItem(
            name, data_source_class, data_source_config_class
        )

    def list(self) -> Collection[DataSourceRegistryItem]:
        return self.__data_source_registry.values()

    def create_data_source(self, name: str) -> IDataSource:
        registry_item = self.__get_source_item(name)

        instance = registry_item.instance_class()
        return instance

    def create_configuration(self, name: str, config_data: Dict[str, Any]):
        registry_item = self.__get_source_item(name)
        instance = config.create_config_from_dict(
            registry_item.config_class, config_data
        )
        return instance

    def __get_source_item(self, name) -> DataSourceRegistryItem:
        registry_item = self.__data_source_registry.get(name)
        if not registry_item:
            raise DataSourceNotFoundException(
                name, list(self.__data_source_registry.keys())
            )
        return registry_item


def register_data_source(name: str, config_class: Type[IDataSourceConfiguration]):
    def inner_decorator(data_source_class: Type[IDataSource]):
        SingletonDataSourceFactory().register_data_source(
            name, data_source_class, config_class
        )
        return data_source_class

    return inner_decorator
