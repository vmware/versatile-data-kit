# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock

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


class AppendTemplatePlugin:
    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.templates.add_template(
            "append",
            pathlib.Path(
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "template-append",
                )
            ),
        )


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_job_with_template():

    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin, AppendTemplatePlugin())

    result: Result = runner.invoke(["run", util.job_path("job-using-templates")])

    cli_assert_equal(0, result)
    assert db_plugin.db.execute_query("select count(1) from dim_vm")[0][0] == 5
