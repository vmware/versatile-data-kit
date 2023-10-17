# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass
from dataclasses import field
from dataclasses import is_dataclass
from dataclasses import MISSING
from typing import Any
from typing import Optional
from typing import Type


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
    :param kwargs: Additional arguments passed to :func:`dataclass`.
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


def __check_config_class(cls):
    if not hasattr(cls, "config_group_description"):
        raise ValueError(f"cls {cls} is not decorated with @config_class.")


def get_config_class_group(cls):
    __check_config_class(cls)
    return getattr(cls, "config_group_name")


def get_config_class_description(cls):
    __check_config_class(cls)
    return getattr(cls, "config_group_description")


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


def get_config_field_metadata(cls, field_name: str):
    __check_config_class(cls)
    return ConfigFieldMetadata(cls, field_name)
