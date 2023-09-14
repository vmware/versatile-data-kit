# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import sqlparse
from vdk.api.job_input import IJobInput
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.file_based_step import StepFuncFactory
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_SQL
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.builtin_plugins.run.step import StepBuilder


class SqlStepSplitterPlugin:
    @hookimpl(trylast=True)
    def initialize_job(self, context: JobContext):
        """
        This is hook implementation that will split SQL file into multiple ones
        treating each sql statement as separate step
        :return:
        """
        new_step_builder = StepBuilder()
        current_steps = context.step_builder.get_steps()

        for potential_step_file in context.job_directory.iterdir():
            for connection_type in context.connections.list_supported_connections():
                if potential_step_file.name.endswith(f"sql.{connection_type}"):
                    step = Step(
                        name=potential_step_file.name,
                        type=TYPE_SQL,
                        runner_func=StepFuncFactory.run_sql_step,
                        file_path=potential_step_file,
                        job_dir=context.job_directory,
                    )
                    current_steps.append(step)

        current_steps.sort(key=lambda x: x.name)
        for step in current_steps:
            new_step_builder.add_step(step)
        context.step_builder = new_step_builder
