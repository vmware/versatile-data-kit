# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from dataclasses import MISSING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar


def config_class(name: str, description: str, **kwargs):
    """
    A decorator to mark a class as a configuration class. It extends dataclass decorator with config related options.
    Each field in a decorator class must be defined with config_field

    Example::

        @config_class(name="group", description="Just example")
        ExampleConfig:
            option1: int = config_field(description="Option 1")
            option2: bool = config_filed(description="Option 2")

    :param name: The name of the configuration group representing by the class.
    :param description: The description of the configuration group.
    :param kwargs: Additional arguments passed same as arguments of :func:`dataclass`.
    """

    def decorator(cls):
        cls = dataclass(cls, **kwargs)

        setattr(cls, "config_group_name", name)
        setattr(cls, "config_group_description", description)

        for field_name, field_info in cls.__dataclass_fields__.items():
            if "config_description" not in field_info.metadata:
                raise TypeError(
                    f"The field '{field_name}' must be declared using config_field."
                )

        return cls

    return decorator


def config_field(
    *,
    description: str,
    is_sensitive: bool = False,
    default=MISSING,
    init=True,
    repr=True,
    hash=None,
    compare=True,
    metadata=None,
    **kwargs,
):
    """
    Define a field within a configuration class. This is extending dataclass.field with addition parameters

    :param description: Description of the configuration field.
    :param is_sensitive: Indicates if the configuration field contains sensitive information.
    The rest are the same as in dataclass.field()
    """

    if metadata is None:
        metadata = {}
    metadata.update(
        {"config_description": description, "config_is_sensitive": is_sensitive}
    )

    return field(
        **kwargs,
        default=default,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
    )


class ConfigFieldMetadata:
    """
    Metadata class for configuration fields.

    Provides methods to access the metadata of a specific configuration field.
    """

    def __init__(self, field_class, field_name: str):
        self._field_name = field_name
        self._field_class = field_class

    def __get_field_metadata_value(self, metadata_key: str) -> Any:
        return self._field_class.__dataclass_fields__[self._field_name].metadata.get(
            metadata_key, None
        )

    def name(self) -> str:
        return self._field_name

    def description(self) -> str:
        return self.__get_field_metadata_value("config_description")

    def is_sensitive(self) -> bool:
        return self.__get_field_metadata_value("config_is_sensitive")

    def default(self) -> Optional[Any]:
        default_value = self._field_class.__dataclass_fields__[self._field_name].default
        return default_value if default_value != MISSING else None


class ConfigClassMetadata:
    """
    Metadata class for configuration classes.

    Provides methods to access the metadata of a specific configuration class.
    """

    def __init__(self, cls: Type):
        self._config_cls: Type[config_class] = cls
        self.__check_config_class()

    def __check_config_class(self):
        if not hasattr(self._config_cls, "config_group_description"):
            raise ValueError(
                f"cls {self._config_cls} is not decorated with @config_class."
            )

    def get_group_name(self) -> str:
        return getattr(self._config_cls, "config_group_name")

    def get_description(self) -> str:
        return getattr(self._config_cls, "config_group_description")

    def get_config_fields(self) -> List[ConfigFieldMetadata]:
        fields_meta = []
        for field_info in fields(self._config_cls):
            fields_meta.append(ConfigFieldMetadata(self._config_cls, field_info.name))
        return fields_meta


T = TypeVar("T")


def is_config_class(cls: Type):
    return ConfigClassMetadata(cls) is not None


def create_config_from_dict(config_class: Type[T], config_data: Dict[str, Any]) -> T:
    field_types = {f.name: f.type for f in fields(config_class)}
    processed_data = {}

    for key, value in config_data.items():
        if hasattr(field_types[key], "__dataclass_fields__"):
            # Nested dataclass
            processed_data[key] = create_config_from_dict(field_types[key], value)
        else:
            processed_data[key] = value

    return config_class(**processed_data)
