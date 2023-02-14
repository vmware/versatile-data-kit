# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock

from vdk.internal.builtin_plugins.job_properties.inmemproperties import (
    InMemPropertiesServiceClient,
)
from vdk.internal.builtin_plugins.job_properties.properties_router import (
    PropertiesRouter,
)
from vdk.internal.builtin_plugins.run.data_job import JobArguments
from vdk.internal.builtin_plugins.run.job_input import JobInput
from vdk.internal.core.config import Configuration


def _get_properties_in_memory():
    router = PropertiesRouter("foo", Configuration({}, {}))
    router.set_properties_factory_method(
        "default", lambda: InMemPropertiesServiceClient()
    )
    return router


def test_substitute_int_arg():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict(param=1)),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == "select 1"


def test_substitute_string_arg():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict(param="table_name")),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select from {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == "select from table_name"


def test_substitute_bool_arg():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict(param=True)),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select from {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == "select from True"


def test_substitute_none_arg():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict(param=None)),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select from {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == "select from None"


def test_substitute_nested_dict_arg():
    nested_dict = dict(y="table_name")
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict(param=nested_dict)),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select from {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == f"select from {nested_dict}"


def test_substitute_object_arg():
    obj = object()
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict(param=obj)),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select from {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == f"select from {obj}"


def test_substitute_empty_args():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict()),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select from {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == query


def test_substitute_none_args():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(None),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select from {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == query


def test_substitute_bool_args():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(True),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select from {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == query


def test_substitute_object_args():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(object()),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    query = "select from {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == query


def test_substitute_params_from_args_with_props():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict(param=1)),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        _get_properties_in_memory(),
    )
    job_input.set_all_properties(dict(not_used="table_name"))
    query = "select {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == "select 1"


def test_substitute_params_from_props_without_args():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        _get_properties_in_memory(),
    )
    job_input.set_all_properties(dict(param=1))
    query = "select {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == "select 1"


def test_substitute_params_from_props_with_args():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict(not_used="table_name")),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        _get_properties_in_memory(),
    )
    job_input.set_all_properties(dict(param=1))
    query = "select {param}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == "select 1"


def test_substitute_params_from_props_and_args():
    job_input = JobInput(
        MagicMock(),
        MagicMock(),
        MagicMock(),
        JobArguments(dict(param_from_args="table_name")),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        _get_properties_in_memory(),
    )
    job_input.set_all_properties(dict(param_from_props="schema_name"))
    query = "select * from {param_from_props}.{param_from_args}"
    result = job_input._substitute_query_params(query).strip("\n")

    assert result == "select * from schema_name.table_name"
