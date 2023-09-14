# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import sqlparse
from vdk.api.job_input import IJobInput
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_SQL
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.builtin_plugins.run.step import StepBuilder


class SqlStatementStep(Step):
    def __init__(self, sql_statement: str, **parent_step_args):
        super().__init__(**parent_step_args)
        self.sql_statement = sql_statement


def run_sql_statement_step(step: SqlStatementStep, job_input: IJobInput) -> bool:
    """Execute single SQL query"""
    job_input.execute_query(step.sql_statement)
    return True


class SqlStepSplitterPlugin:
    @staticmethod
    def __split_sql_step(step_builder: StepBuilder, original_step: Step):
        sql_file_path: pathlib.Path = pathlib.Path(original_step.file_path)
        if sql_file_path.is_file():
            sql_statement = sql_file_path.read_text()
            sql_statement_strings = sqlparse.split(sql_statement)
            for i, sql in enumerate(sql_statement_strings):
                sql_statement_step = SqlStatementStep(
                    name=f"{sql_file_path.name}-sql-{i+1}",
                    type="sql-statement",
                    runner_func=run_sql_statement_step,
                    file_path=original_step.file_path,
                    job_dir=original_step.job_dir,
                    parent=original_step,
                    sql_statement=sql,
                )
                step_builder.add_step(sql_statement_step)
        else:
            step_builder.add_step(original_step)

    @hookimpl(trylast=True)
    def initialize_job(self, context: JobContext):
        """
        This is hook implementation that will split SQL file into multiple ones
        treating each sql statement as separate step
        :return:
        """
        new_step_builder = StepBuilder()
        for step in context.step_builder.get_steps():
            if step.type == TYPE_SQL:
                self.__split_sql_step(new_step_builder, step)
            else:
                new_step_builder.add_step(step)
        context.step_builder = new_step_builder
