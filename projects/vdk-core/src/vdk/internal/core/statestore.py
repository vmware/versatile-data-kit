# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import cast
from typing import Generic
from typing import Optional
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class StoreKey(Generic[T]):
    """StoreKey is an object used as a key to a Store.

    A StoreKey is associated with the type T of the value of the key.
    """

    key: str


class ImmutableStoreKey(StoreKey[T]):
    """
    StoreKey associated with value which is considered immutable once set.

    Trying to set it again will produce error and raise exception.
    The value itself may or may not be immutable.
    """

    pass


# TODO(minor): should be enum but in python 3.7 and 3.8 cannot declare enum with generic data types
# TODO(minor): also if enum perhaps we do not need string value e.g OP_ID = StoreKey[str]() would be better.
class CommonStoreKeys:
    """
    StoreKeys for a common (standard) attributes used during lifetime of the CLI.
    """

    """
    OpID is similar to trace ID in open tracing.
    It enable tracing multiple operations across difference services and datasets
    """
    OP_ID: StoreKey[str] = StoreKey[str]("vdk.op_id")
    """
    Execution ID is the current id of the current execution.
    It can be passed externally (e.g in case of external re-tries are  considered part of 1 execution)
    """
    EXECUTION_ID: StoreKey[str] = StoreKey[str]("vdk.execution_id")
    """
    It may be the same as Execution_ID unless re-tries per executions are supported
    """
    ATTEMPT_ID: StoreKey[str] = StoreKey[str]("vdk.attempt_id")

    """
    When the CLI (and hence job) execution has been started
    """
    START_TIME: StoreKey[datetime] = StoreKey[datetime]("vdk.start_time")
    """
    When the CLI (and hence job) execution has finished
    """
    END_TIME: StoreKey[datetime] = StoreKey[datetime]("vdk.end_time")

    """
    Build information about the CLI:
    """
    VDK_VERSION: StoreKey[str] = ImmutableStoreKey[str]("vdk.vdk_version")


class StateStore:
    """
    StateStore is a type-safe heterogeneous mapping that allows keys and value types to be defined to keep state of app.

    It is meant to keeps state of the current CLI execution.
    Contains data like opId, executionID, start time, end time, steps executed, etc.
    Telemetry, logging, monitoring, etc. facilities read data from this class and re-model the data to suit their
    needs.

    If a module wants to store data in this StateStore, it creates StoreKeys:

    .. highlight:: python
    .. code-block:: python

        key_with_string_value = StoreKey[str]()
        key_with_bool_value = StoreKey[bool]()

    To store data:

    .. code-block:: python

        # Value type must match the key.
        store[key_with_string_value] = "value"
        store[key_with_bool_value] = True

    To retrieve the data:

    .. code-block:: python

        # The type of string_value is str.
        string_value = store[key_with_string_value]
        # The type of bool_value is bool.
        bool_value = store[key_with_bool_value]

    """

    def __init__(self, store: dict[StoreKey[Any], object] = None) -> None:
        self.__store = {} if store is None else store

    def __setitem__(self, key: StoreKey[T], value: T) -> None:
        """Set a value for key."""
        self.__check_for_immutable_key_existance(key)
        self.__store[key] = value

    def __check_for_immutable_key_existance(self, key: StoreKey[T]) -> None:
        if isinstance(key, ImmutableStoreKey):
            if key in self.__store:
                raise AttributeError(
                    f"Cannot update value for key {key} because key is immutable "
                    f"and value with that key already exists."
                )

    def __getitem__(self, key: StoreKey[T]) -> T:
        """Get the value for key.

        Raises ``KeyError`` if the key wasn't set before.
        """
        return cast(T, self.__store[key])

    def get(self, key: StoreKey[T], default: T = None) -> T | None:
        """Get the value for key, or return default if the key wasn't set before."""
        try:
            return self[key]
        except KeyError:
            return default

    def set(self, key: StoreKey[T], value: T) -> None:
        """Set a value for the given key."""
        self[key] = value

    def __delitem__(self, key: StoreKey[T]) -> None:
        """Delete the value for key.

        Raises ``KeyError`` if the key wasn't set before.
        Raises ``AttributeError`` if the key is set and is immutable.
        """
        self.__check_for_immutable_key_existance(key)
        del self.__store[key]

    def __contains__(self, key: StoreKey[T]) -> bool:
        """Return whether key was set."""
        return key in self.__store

    def __repr__(self) -> str:
        """Return string representation of the state store"""
        return self.__store.__repr__()

    def clone(self) -> StateStore:
        """Returns a new statestore object that is a copy of this instance.
        Clone performs shallow copy - only the top-level objects are duplicated and the lower levels contain references
        """
        store_copy = self.__store.copy()
        return StateStore(store_copy)
