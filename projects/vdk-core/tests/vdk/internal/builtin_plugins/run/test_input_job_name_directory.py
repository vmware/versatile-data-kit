# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib
from unittest.mock import MagicMock

from vdk.internal.builtin_plugins.run.job_input import JobInput


def test_job_name_propagation():
    name = "test_name"
    job_input = JobInput(
        name,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )

    assert job_input.get_name() == name


def test_job_directory_propagation():
    job_directory = pathlib.Path(__file__).parent.resolve()
    job_input = JobInput(
        MagicMock(),
        job_directory,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )

    assert job_input.get_job_directory() == job_directory
