# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
from dataclasses import dataclass
from datetime import datetime
from typing import cast
from typing import Dict
from typing import Optional

from taurus.api.job_input import IJobArguments
from taurus.api.plugin.core_hook_spec import JobRunHookSpecs
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.run.execution_results import ExecutionResult
from taurus.vdk.builtin_plugins.run.execution_results import StepResult
from taurus.vdk.builtin_plugins.run.file_based_step import JobFilesLocator
from taurus.vdk.builtin_plugins.run.file_based_step import StepFuncFactory
from taurus.vdk.builtin_plugins.run.file_based_step import TYPE_PYTHON
from taurus.vdk.builtin_plugins.run.file_based_step import TYPE_SQL
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.builtin_plugins.run.run_status import ExecutionStatus
from taurus.vdk.builtin_plugins.run.step import Step
from taurus.vdk.core import errors
from taurus.vdk.core.context import CoreContext
from taurus.vdk.core.statestore import CommonStoreKeys

log = logging.getLogger(__name__)


@dataclass
class JobArguments(IJobArguments):
    arguments: Dict

    def get_arguments(self) -> dict:
        return self.arguments


class DataJobFactory:
    @staticmethod
    def new_datajob(
        data_job_directory: Optional[pathlib.Path],
        core_context: CoreContext,
        name: Optional[str] = None,
    ):
        """
        Create a new data job
        :param data_job_directory: the source code of the data job that will be executed
        :param core_context: Core context of the CLI. Upon run , the data job will span child context to keep its context/state
        :param name: the name of the job. Leave it out and it will be infered from the directory name.
        """
        return DataJob(data_job_directory, core_context, name)


class DataJobDefaultHookImplPlugin:
    """
    Default implementation of main plugin hooks in Data Job Run Cycle.
    Plugins may decorate or replace some of the implementations
    """

    @staticmethod
    @hookimpl(trylast=True)
    def run_step(context: JobContext, step: Step) -> StepResult:
        start_time = datetime.utcnow()
        exception = None
        details = None

        try:
            log.debug(f"Processing step {step.name} ...")
            step_executed = step.runner_func(step, context.job_input)
            log.debug("Processing step %s completed successfully" % step.name)
            status = (
                ExecutionStatus.SUCCESS
                if step_executed
                else ExecutionStatus.NOT_RUNNABLE
            )
        except BaseException as e:
            status = ExecutionStatus.ERROR
            details = errors.MSG_WHY_FROM_EXCEPTION(e)
            blamee = errors.find_whom_to_blame_from_exception(e)
            exception = e
            errors.log_exception(
                blamee,
                log,
                what_happened=f"Processing step {step.name} completed with error.",
                why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                consequences="I will not process the remaining steps (if any), "
                "and this Data Job execution will be marked as failed.",
                countermeasures="See exception and fix the root cause, so that the exception does "
                "not appear anymore.",
                exception=e,
            )

        return StepResult(
            name=step.name,
            type=step.type,
            start_time=start_time,
            end_time=datetime.utcnow(),
            status=status,
            details=details,
            exception=exception,
        )

    @staticmethod
    @hookimpl(trylast=True)
    def run_job(context: JobContext) -> ExecutionResult:
        """The script that runs the actual run of the data job.
        It executes the provided steps starting from context.степс in sequential order
        """
        start_time = datetime.utcnow()
        execution_status = None
        exception = None
        step_results = []
        try:
            execution_status = ExecutionStatus.SUCCESS
            for current in context.step_builder.get_steps():
                res = context.core_context.plugin_registry.hook().run_step(
                    context=context, step=current
                )
                step_results.append(res)
                # errors.clear_intermediate_errors()  # step completed successfully, so we can forget errors
                if res.status == ExecutionStatus.ERROR:
                    execution_status = ExecutionStatus.ERROR
                    exception = res.exception
                    break
        except BaseException as e:
            exception = e

        execution_result = ExecutionResult(
            context.name,
            context.core_context.state.get(CommonStoreKeys.EXECUTION_ID),
            start_time,
            datetime.utcnow(),
            execution_status,
            exception,
            step_results,
        )
        return execution_result

    @staticmethod
    @hookimpl
    def initialize_job(context: JobContext):
        # TODO: consider split into collect_steps hooks for better clarity and ease.
        # though let's first gather some data on how useful such new hooks would be.
        if context.job_directory is None:
            log.info(
                "Data Job directory is not specified. Default job initialization will be skipped."
            )
            return

        file_locator: JobFilesLocator = JobFilesLocator()
        script_files = file_locator.get_script_files(context.job_directory)

        for file_path in script_files:
            if file_path.name.lower().endswith(".sql"):
                step = Step(
                    name=file_path.name,
                    type=TYPE_SQL,
                    runner_func=StepFuncFactory.run_sql_step,
                    file_path=file_path,
                    job_dir=context.job_directory,
                )
            elif file_path.name.lower().endswith(".py"):
                # TODO: check for run method.
                step = Step(
                    name=file_path.name,
                    type=TYPE_PYTHON,
                    runner_func=StepFuncFactory.run_python_step,
                    file_path=file_path,
                    job_dir=context.job_directory,
                )
            else:
                log.info("Skipping file as it is not a valid job step: %s" % file_path)
                continue
            context.step_builder.add_step(step)

    @staticmethod
    @hookimpl
    def finalize_job(context: JobContext):
        pass


class DataJob:
    """
    Object representing a data job.
    Data Job is abstraction representing definition of a data job set by data engineer.
    Data Job is a sequence of steps executed in a certain order.
    Data JOb run cycle is encapsulated by run method.

    Prefer to use DataJobFactory to create new data job.
    """

    def __init__(
        self,
        data_job_directory: Optional[pathlib.Path],
        core_context: CoreContext,
        name: Optional[str] = None,
    ):
        if data_job_directory is None and name is None:
            raise ValueError(
                "Cannot initialize DataJob. "
                "At least one of data job directory or data job name need to be set. "
            )
        self._name = data_job_directory.name if name is None else name
        self._data_job_directory = data_job_directory
        """
        We need to create child context which will contain only for this job execution.
        This is since we want to have multiple job executions within same process (for example templates executions)
        """
        self._core_context = core_context.create_child_context()
        self._plugin_hook = cast(
            JobRunHookSpecs, self._core_context.plugin_registry.hook()
        )

    @property
    def name(self):
        return self._name

    # TODO: this also can be a hook - e.g job run_cycle_algorithm
    def run(self, args: Dict = None) -> ExecutionResult:
        """
        This is basic implementation of Data Job run(execution) cycle algorithm.
        All stages are pluggable as hooks.
         * Initialize - Initialize job's main functionalities -e.g database connections,logging,collecting steps, etc.
         * Run Job -Takes care of starting and running a data job
         * Run steps - run the actual steps. This is where hte user code will be invoked.
         * Finalize - after the job finishes, do any finalization -clean up, send monitoring, etc.
        """
        if args is None:
            args = {}

        if not self._core_context.plugin_registry.has_plugin(
            DataJobDefaultHookImplPlugin.__name__
        ):
            self._core_context.plugin_registry.load_plugin_with_hooks_impl(
                DataJobDefaultHookImplPlugin(), DataJobDefaultHookImplPlugin.__name__
            )

        from taurus.vdk.builtin_plugins.templates.template_impl import TemplatesImpl

        job_context = JobContext(
            name=self._name,
            job_directory=self._data_job_directory,
            core_context=self._core_context,
            job_args=JobArguments(args),
            templates=TemplatesImpl(
                job_name=self.name, core_context=self._core_context
            ),
        )
        self._plugin_hook.initialize_job(context=job_context)
        try:
            return self._plugin_hook.run_job(context=job_context)
        finally:
            self._plugin_hook.finalize_job(context=job_context)
