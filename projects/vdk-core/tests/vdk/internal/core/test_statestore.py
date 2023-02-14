# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass

import pytest
from vdk.internal.core.statestore import ImmutableStoreKey
from vdk.internal.core.statestore import StateStore
from vdk.internal.core.statestore import StoreKey


def test_statestore_add_new() -> None:
    store = StateStore()

    key = StoreKey[str]("key")

    assert key not in store
    assert store.get(key, "default") == "default"
    store[key] = "value"
    assert key in store
    assert store[key] == "value"
    assert store.get(key, None) == "value"
    store.set(key, "new_value")
    assert store[key] == "new_value"

    # mypy enforces type correctness
    _ = store[key] + "string"


def test_statestore_delete_key() -> None:
    store = StateStore()
    key = StoreKey[str]("key")

    store[key] = "value"
    del store[key]
    assert key not in store

    with pytest.raises(KeyError):
        _ = store[key]

    with pytest.raises(KeyError):
        del store[key]


def test_statestore_multiple_keys() -> None:
    store = StateStore()

    key_string = StoreKey[str]("key_string")
    key_int = StoreKey[int]("key_int")

    store[key_string] = "value"
    assert key_string in store
    assert key_int not in store
    assert store.get(key_int, None) is None
    with pytest.raises(KeyError):
        _ = store[key_int]

    # mypy enforces type correctness
    with pytest.raises(KeyError):
        del store[key_int]
    store[key_int] = 2
    _ = store[key_int] + 3

    with pytest.raises(TypeError):
        _ = store[key_int] + "str"


def test_statestore_immutable() -> None:
    store = StateStore()

    immutable_key = ImmutableStoreKey[int]("key")
    assert immutable_key not in store
    store[immutable_key] = 42

    with pytest.raises(AttributeError):
        store[immutable_key] = 69
    with pytest.raises(AttributeError):
        store.set(immutable_key, 69)
    with pytest.raises(AttributeError):
        store.__setitem__(immutable_key, 69)


def test_statorestore_multiple_statestores() -> None:
    store = StateStore()
    key = StoreKey[int]("key")
    store[key] = 1

    store2 = StateStore()
    key2 = StoreKey[int]("key2")

    assert key not in store2
    assert key2 not in store

    store2[key] = 1000
    store2[key2] = 2000

    assert store2.get(key) == 1000
    assert store.get(key) == 1
    assert store2.get(key2) == 2000


def test_statestore_classes() -> None:
    @dataclass
    class Foo:
        bar: float

    store = StateStore()

    class TestStoreKeys:
        MY_INT = StoreKey[int]("my_int")
        MY_FOO = StoreKey[Foo]("my_foo")

    store[TestStoreKeys.MY_INT] = 1
    store[TestStoreKeys.MY_FOO] = Foo(3.14)

    with pytest.raises(TypeError):
        _ = store[TestStoreKeys.MY_INT] + "str"


def test_statestore_repr() -> None:
    store = StateStore()
    store[StoreKey[int]("key")] = 1  # primitive value
    store[StoreKey[int]("nested")] = store  # make sure we handle recursion

    assert store.__repr__() == "{StoreKey(key='key'): 1, StoreKey(key='nested'): {...}}"


def test_statestore_clone() -> None:
    original_store = StateStore()

    key_string = StoreKey[str]("key_string")

    original_store[key_string] = "original-value"

    cloned_store = original_store.clone()

    assert cloned_store.get(key_string) == "original-value"

    cloned_store[key_string] = "updated-value"

    assert cloned_store[key_string] == "updated-value"
    assert original_store[key_string] == "original-value"

    new_key = StoreKey[int]("key_int")
    cloned_store[new_key] = 1

    assert cloned_store[new_key] == 1
    assert new_key not in original_store
