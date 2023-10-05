# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib
from unittest.mock import MagicMock

import pytest
from vdk.internal.builtin_plugins.run.data_job import DataJob
from vdk.internal.builtin_plugins.run.data_job import DataJobFactory
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.run_status import ExecutionStatus
from vdk.internal.builtin_plugins.templates.template_impl import TemplatesImpl
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import ErrorType
from vdk.internal.core.errors import UserCodeError


def test_template_builder():
    templates = TemplatesImpl(
        "foo", MagicMock(spec=CoreContext), MagicMock(spec=DataJobFactory)
    )
    templates.add_template("name", pathlib.Path("/tmp/template"))

    assert str(templates.get_template_directory("name")) == "/tmp/template"


def test_template_builder_overwrite():
    templates = TemplatesImpl(
        "foo", MagicMock(spec=CoreContext), MagicMock(spec=DataJobFactory)
    )
    templates.add_template("name", pathlib.Path("/tmp/template"))
    templates.add_template("name", pathlib.Path("/tmp/new-location"))

    assert str(templates.get_template_directory("name")) == "/tmp/new-location"


def test_template_execute():
    mock_job_factory = MagicMock(spec=DataJobFactory)
    mock_job = MagicMock(spec=DataJob)
    mock_job.run.return_value = ExecutionResult(
        "foo", "1", None, None, ExecutionStatus.SUCCESS, [], None, None
    )
    mock_job_factory.new_datajob.return_value = mock_job
    mock_context = MagicMock(spec=CoreContext)
    templates = TemplatesImpl("foo", mock_context, mock_job_factory)
    templates.add_template("name", pathlib.Path("/tmp/template"))

    templates.execute_template("name", {"arg": "value"})

    mock_job_factory.new_datajob.assert_called_once_with(
        pathlib.Path("/tmp/template"), mock_context, name="foo"
    )


def test_template_execute_template_fails_raise_exception():
    mock_job_factory = MagicMock(spec=DataJobFactory)
    mock_job = MagicMock(spec=DataJob)
    mock_job.run.return_value = ExecutionResult(
        "foo",
        "1",
        None,
        None,
        ExecutionStatus.ERROR,
        [],
        AttributeError("dummy"),
        ErrorType.USER_ERROR,
    )
    mock_job_factory.new_datajob.return_value = mock_job
    mock_context = MagicMock(spec=CoreContext)
    templates = TemplatesImpl("foo", mock_context, mock_job_factory)
    templates.add_template("name", pathlib.Path("/tmp/template"))

    # TODO: test for more specif
    with pytest.raises(Exception):
        templates.execute_template("name", {"arg": "value"})


def test_template_execute_no_such():
    mock_job_factory = MagicMock(spec=DataJobFactory)
    mock_context = MagicMock(spec=CoreContext)
    templates = TemplatesImpl("foo", mock_context, mock_job_factory)
    templates.add_template("name", pathlib.Path("/tmp/template"))

    with pytest.raises(UserCodeError):
        templates.execute_template("no-such", {"arg": "value"})
