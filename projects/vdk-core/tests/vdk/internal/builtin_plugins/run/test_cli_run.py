# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import pathlib
from unittest.mock import MagicMock

import py
import pytest
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.cli_run import CliRunImpl
from vdk.internal.builtin_plugins.run.data_job import DataJob
from vdk.internal.builtin_plugins.run.data_job import DataJobFactory
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.core.config import Configuration
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.statestore import StateStore


@pytest.fixture
def mock_job_factory(is_failed: bool, exception: BaseException) -> DataJobFactory:
    mock_job = MagicMock(spec=DataJob)
    mock_execution_result = MagicMock(spec=ExecutionResult)
    mock_job.run.return_value = mock_execution_result
    mock_execution_result.is_failed.return_value = is_failed
    if exception:
        mock_execution_result.get_exception_to_raise.return_value = exception
    job_factory = MagicMock(spec=DataJobFactory)
    job_factory.new_datajob.return_value = mock_job
    return job_factory


@pytest.mark.parametrize("is_failed, exception", [(False, None)])
def test_run_job(tmpdir: py.path.local, mock_job_factory: DataJobFactory):
    job_folder = pathlib.Path(tmpdir.mkdir("job"))
    context = CoreContext(
        MagicMock(spec=IPluginRegistry),
        MagicMock(spec=Configuration),
        MagicMock(spec=StateStore),
    )

    run_impl = CliRunImpl(mock_job_factory)
    run_impl.create_and_run_data_job(
        context=context, data_job_directory=job_folder, arguments=None
    )


@pytest.mark.parametrize("is_failed, exception", [(True, IndexError("foo"))])
def test_run_job_failed(tmpdir, mock_job_factory):
    job_folder = pathlib.Path(tmpdir.mkdir("job"))
    context = CoreContext(
        MagicMock(spec=IPluginRegistry),
        MagicMock(spec=Configuration),
        MagicMock(spec=StateStore),
    )

    run_impl = CliRunImpl(mock_job_factory)

    with pytest.raises(IndexError):
        run_impl.create_and_run_data_job(
            context=context, data_job_directory=job_folder, arguments=None
        )


@pytest.mark.parametrize("is_failed, exception", [(False, None)])
def test_run_job_arguments(tmpdir: py.path.local, mock_job_factory: DataJobFactory):
    job_folder = pathlib.Path(tmpdir.mkdir("job"))
    context = CoreContext(
        MagicMock(spec=IPluginRegistry),
        MagicMock(spec=Configuration),
        MagicMock(spec=StateStore),
    )
    args = {"arg_1": "one", "arg_2": 2, "nested": {"nested_true": True}}
    args_as_json = json.dumps(args)

    run_impl = CliRunImpl(mock_job_factory)
    run_impl.create_and_run_data_job(
        context=context, data_job_directory=job_folder, arguments=args_as_json
    )

    mock_job_factory.new_datajob().run.assert_called_once_with(args)


@pytest.mark.parametrize("is_failed, exception", [(False, None)])
def test_run_job_invalid_arguments(
    tmpdir: py.path.local, mock_job_factory: DataJobFactory
):
    job_folder = pathlib.Path(tmpdir.mkdir("job"))
    context = CoreContext(
        MagicMock(spec=IPluginRegistry),
        MagicMock(spec=Configuration),
        MagicMock(spec=StateStore),
    )
    args_as_json = "arg_1=one,arg_2=2"

    run_impl = CliRunImpl(mock_job_factory)
    with pytest.raises(UserCodeError):
        run_impl.create_and_run_data_job(
            context=context, data_job_directory=job_folder, arguments=args_as_json
        )
