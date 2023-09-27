# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
from unittest import mock

from click.testing import Result
from functional.run import util
from vdk.internal.core import errors
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_run_successful(tmpdir):
    output_path = pathlib.Path(str(tmpdir)).joinpath("summary.json")
    with mock.patch.dict(os.environ, {"JOB_RUN_SUMMARY_FILE_PATH": str(output_path)}):
        runner = CliEntryBasedTestRunner()

        result: Result = runner.invoke(["run", util.job_path("simple-job")])

        cli_assert_equal(0, result)

    assert output_path.exists()
    output = json.loads(output_path.read_text())
    assert output.get("status") == "success"


def test_run_error(tmpdir):
    errors.resolvable_context().clear()
    output_path = pathlib.Path(str(tmpdir)).joinpath("summary.json")
    with mock.patch.dict(os.environ, {"JOB_RUN_SUMMARY_FILE_PATH": str(output_path)}):
        runner = CliEntryBasedTestRunner()

        result: Result = runner.invoke(["run", util.job_path("fail-job")])
        cli_assert_equal(1, result)

    assert output_path.exists()
    output = json.loads(output_path.read_text())

    assert output.get("status") == "error"
    assert output.get("blamee") == "User Error"
    assert output.get("details") == "cannot do math :("

    assert len(output["steps"]) == 1
    assert output["steps"][0].get("name") == "1_step.py"

    errors.resolvable_context().clear()
