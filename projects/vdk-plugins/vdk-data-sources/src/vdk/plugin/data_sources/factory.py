# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import Collection
from typing import Dict
from typing import List
from typing import Type

from vdk.plugin.data_sources import config
from vdk.plugin.data_sources.data_source import IDataSource
from vdk.plugin.data_sources.data_source import (
    IDataSourceConfiguration,
)


def data_source(name: str, config_class: Type[IDataSourceConfiguration]):
    def inner_decorator(data_source_class: Type[IDataSource]):
        data_source_class.__data_source_name__ = name
        data_source_class.__data_source__config__class__ = config_class
        return data_source_class

    return inner_decorator


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


class IDataSourceFactory:
    @abstractmethod
    def register_data_source_class(
        self,
        data_source_class: Type[IDataSource],
    ):
        """
        Register a data source and its associated configuration class.

        :param data_source_class: The data source class that implements `IDataSource` and must be decoreated with @data_source

        Example::

        @data_source(name="csv", config_class=CsvDataSourceConfiguration)
        class CsvDataSource(IDataSource):
            ...
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

    def register_data_source_class(self, data_source_class: Type[IDataSource]):
        if not hasattr(data_source_class, "__data_source_name__") or not hasattr(
            data_source_class, "__data_source__config__class__"
        ):
            raise ValueError(
                "Invalid data_source_class."
                "data_source_class must extend IDataSource, and be decorated with @data_source."
            )

        name = getattr(data_source_class, "__data_source_name__")
        config_class = getattr(data_source_class, "__data_source__config__class__")
        self.__register_data_source(name, data_source_class, config_class)

    def __register_data_source(
        self,
        name: str,
        data_source_class: Type[IDataSource],
        data_source_config_class: Type[IDataSourceConfiguration],
    ):
        if not isinstance(data_source_class, type):
            raise ValueError(
                "data_source_class must a class definition. Not a class instance for example."
            )
        if not issubclass(data_source_class, IDataSource):
            raise ValueError("data_source_class must be a class inheriting IDataSource")
        if not isinstance(data_source_config_class, type):
            raise ValueError(
                "data_source_config_class must a class definition. Not a class instance for example."
            )
        if not issubclass(data_source_config_class, IDataSourceConfiguration):
            raise ValueError(
                "data_source_config_class must be a class inheriting IDataSourceConfiguration"
            )

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
