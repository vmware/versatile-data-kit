# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from functional.run import util
from functional.run.test_run_sql_queries import VDK_DB_DEFAULT_TYPE
from functional.run.test_run_templates import TemplatePlugin
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import DB_TYPE_SQLITE_MEMORY
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryDbPlugin


class DecoratorsPlugin:
    def __init__(self):
        self.queries = []
        self.called_templates = []

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        def decorator_execute_query(original_func):
            def wrapper(query_statement, *args, **kwargs):
                self.queries.append(query_statement)
                return original_func(query_statement, *args, **kwargs)

            return wrapper

        def decorator_execute_template(original_func):
            def wrapper(template_name: str, template_args: dict, *args, **kwargs):
                self.called_templates.append(template_name)
                return original_func(template_name, template_args, *args, **kwargs)

            return wrapper

        context.job_input.execute_query = decorator_execute_query(
            context.job_input.execute_query
        )
        context.job_input.execute_template = decorator_execute_template(
            context.job_input.execute_template
        )


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_decorate_execute_query():
    decorator_plugin = DecoratorsPlugin()
    runner = CliEntryBasedTestRunner(decorator_plugin, SqLite3MemoryDbPlugin())

    result: Result = runner.invoke(["run", util.job_path("simple-create-insert")])
    cli_assert_equal(0, result)
    assert len(decorator_plugin.queries) == 2


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_decorate_execute_template():
    decorator_plugin = DecoratorsPlugin()
    runner = CliEntryBasedTestRunner(
        decorator_plugin, SqLite3MemoryDbPlugin(), TemplatePlugin()
    )

    result: Result = runner.invoke(["run", util.job_path("job-using-templates")])
    cli_assert_equal(0, result)
    assert len(decorator_plugin.called_templates) == 1
