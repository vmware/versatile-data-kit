# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
import shutil
from unittest import mock

import py
from click.testing import Result
from functional.run import util
from functional.run.test_run_sql_queries import VDK_DB_DEFAULT_TYPE
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path
from vdk.plugin.test_utils.util_plugins import DB_TYPE_SQLITE_MEMORY
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryDbPlugin


class TemplatePlugin:
    def __init__(
        self,
        template_name: str = "append",
        template_path: pathlib.Path = pathlib.Path(util.job_path("template-append")),
    ):
        self.__template_name = template_name
        self.__template_path = template_path

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.templates.add_template(self.__template_name, self.__template_path)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_job_with_template():
    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin, TemplatePlugin())

    result: Result = runner.invoke(["run", util.job_path("job-using-templates")])

    cli_assert_equal(0, result)
    assert db_plugin.db.execute_query("select count(1) from dim_vm")[0][0] == 5


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_job_with_template_error(tmpdir: py.path.local):
    db_plugin = SqLite3MemoryDbPlugin()

    # break the template by adding fail step
    template_path = pathlib.Path(tmpdir).joinpath("template-append")
    shutil.copytree(util.job_path("template-append"), template_path)
    template_path.joinpath("01_fail.sql").write_text("select * from no_such_table")

    runner = CliEntryBasedTestRunner(db_plugin, TemplatePlugin("append", template_path))

    result: Result = runner.invoke(["run", util.job_path("job-using-templates")])

    cli_assert_equal(1, result)
    assert "no such table: no_such_table" in result.output


def test_run_job_with_cancelled_template():
    """
    Test runs a data job with two steps which in turns runs a template with two steps.
    Every step prints e.g Step 1,2 and Template Step 1,2 etc. After the first template
    step is executed the cancel_job_execution() method is called. Test aims to check
    correct template cancellation (when a template step is cancelled remaining data job
    steps continue)

    Test checks:
    template execution is canceled and all job steps are executed.
    template steps prior to the cancel_job_execution() call are executed.
    proper exit code is set.
    proper message is logged confirming template was cancelled from cancel_job_execution() method.
    :return:
    """
    test_runner = CliEntryBasedTestRunner(
        TemplatePlugin("cancel-job", pathlib.Path(util.job_path("cancel-job")))
    )

    result: Result = test_runner.invoke(["run", util.job_path("cancel-job-template")])

    assert "Step 1." in result.output
    assert "Step 2." in result.output
    assert "Step Cancel 1." in result.output
    assert "Step Cancel 2." in result.output
    assert "Step Cancel 3." not in result.output

    cli_assert_equal(0, result)


def test_exception_propagated_to_user():
    test_runner = CliEntryBasedTestRunner(
        TemplatePlugin("csv-risky", pathlib.Path(util.job_path("template-csv-risky")))
    )
    result: Result = test_runner.invoke(
        ["run", util.job_path("job-using-risky-templates")]
    )
    cli_assert_equal(0, result)
    assert "Handling empty data error" in result.output
