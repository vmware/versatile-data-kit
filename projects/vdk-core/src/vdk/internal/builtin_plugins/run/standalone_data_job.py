# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import logging
import pathlib
import sys
from pathlib import Path
from typing import cast

from vdk.api.data_job import IStandaloneDataJob
from vdk.api.job_input import IJobInput
from vdk.api.plugin.core_hook_spec import CoreHookSpecs
from vdk.api.plugin.core_hook_spec import JobRunHookSpecs
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins import builtin_hook_impl
from vdk.internal.builtin_plugins.internal_hookspecs import InternalHookSpecs
from vdk.internal.builtin_plugins.run.data_job import DataJobDefaultHookImplPlugin
from vdk.internal.builtin_plugins.run.data_job import JobArguments
from vdk.internal.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from vdk.internal.builtin_plugins.run.execution_tracking import ExecutionTrackingPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.builtin_plugins.run.step import StepBuilder
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import StateStore
from vdk.internal.plugin.plugin import PluginRegistry

log = logging.getLogger(__name__)


class NoOpStepDataJobHookImplPlugin(DataJobDefaultHookImplPlugin):
    """
    Implementation that overrides of the functionality of the DataJobDefaultHookImplPlugin
    so that it runs a single NoOp step
    """

    @hookimpl
    def initialize_job(self, context: JobContext):
        step = Step(
            name="NoOpStep",
            type="noop",
            runner_func=lambda _step, _job_input: True,  # Intentional noop
            file_path=Path(__file__),
            job_dir=context.job_directory,
        )
        context.step_builder.add_step(step)


class StandaloneDataJob(IStandaloneDataJob):
    """
    A contextmanager that executes all the necessary "setup" logic needed to return an initialised IJobInput
    object and finalize logic when the context is exited

    Sample usage::

        with StandaloneDataJob(datajob_directory) as job_input:
            #... use job_input object to interact with SuperCollider
    """

    def __init__(
        self,
        data_job_directory: pathlib.Path | None,
        name: str | None = None,
        job_args: dict | None = None,
        extra_plugins: list = [],
        template_name: str | None = None,
    ):
        if data_job_directory is None and name is None:
            raise ValueError(
                "Cannot initialize DataJob. "
                "At least one of data job directory or data job name need to be set. "
            )
        self._name = data_job_directory.name if name is None else name
        self._data_job_directory = data_job_directory
        if job_args is None:
            job_args = {}
        self._job_args = job_args

        self._plugin_registry = PluginRegistry()
        self._plugin_registry.add_hook_specs(InternalHookSpecs)
        for plugin in extra_plugins:
            self._plugin_registry.load_plugin_with_hooks_impl(plugin)
        self._plugin_registry.load_plugins_from_setuptools_entrypoints()
        self._plugin_registry.add_hook_specs(CoreHookSpecs)
        self._plugin_registry.load_plugin_with_hooks_impl(
            builtin_hook_impl, "core-plugin"
        )
        self._template_name = template_name

        command_line_args = ["run", str(data_job_directory)] + (
            ["--arguments", json.dumps(job_args)] if job_args else []
        )
        log.debug(
            f"Pass command line arguments for standalone data job to simulate vdk run: {command_line_args}"
        )
        cast(CoreHookSpecs, self._plugin_registry.hook()).vdk_start.call_historic(
            kwargs=dict(
                plugin_registry=self._plugin_registry,
                command_line_args=command_line_args,
            )
        )

        conf_builder = ConfigurationBuilder()
        cast(CoreHookSpecs, self._plugin_registry.hook()).vdk_configure(
            config_builder=conf_builder
        )
        configuration = conf_builder.build()

        core_context = CoreContext(self._plugin_registry, configuration, StateStore())
        if template_name:
            core_context.state.set(ExecutionStateStoreKeys.TEMPLATE_NAME, template_name)
        core_context.plugin_registry.load_plugin_with_hooks_impl(
            ExecutionTrackingPlugin()
        )
        cast(CoreHookSpecs, self._plugin_registry.hook()).vdk_initialize(
            context=core_context
        )

        self._core_context = core_context
        self._job_context = None

    def __override_with_noop_step(self):
        noop_step = Step(
            name="NoOpStep",
            type="noop",
            runner_func=lambda _step, _job_input: True,  # Intentional noop
            file_path=Path(__file__),
            job_dir=self._job_context.job_directory,
        )
        log.debug(
            f"StandaloneDataJob will ignore following steps of the data job {self._job_context.step_builder}"
        )
        self._job_context.step_builder = StepBuilder()
        self._job_context.step_builder.add_step(noop_step)

    def __enter__(self) -> IJobInput:
        try:
            self._core_context.plugin_registry.load_plugin_with_hooks_impl(
                NoOpStepDataJobHookImplPlugin(), NoOpStepDataJobHookImplPlugin.__name__
            )

            from vdk.internal.builtin_plugins.templates.template_impl import (
                TemplatesImpl,
            )

            self._job_context = JobContext(
                name=self._name,
                job_directory=self._data_job_directory,
                core_context=self._core_context,
                job_args=JobArguments(self._job_args),
                templates=TemplatesImpl(
                    job_name=self._name,
                    core_context=self._core_context,
                    template_name=self._template_name,
                ),
            )

            # We need to call both the initialize_job and run_job hooks to get a fully initialized JobInput
            cast(JobRunHookSpecs, self._plugin_registry.hook()).initialize_job(
                context=self._job_context
            )
            self.__override_with_noop_step()

            cast(JobRunHookSpecs, self._plugin_registry.hook()).run_job(
                context=self._job_context
            )

            return self._job_context.job_input
        except:
            # Ensure __exit__ gets called so the vdk_exception hook can be triggered
            self.__exit__(*sys.exc_info())

    def __exit__(self, exc_type, exc_value, exc_traceback):
        exit_code = 0
        if exc_type:
            handled = cast(CoreHookSpecs, self._plugin_registry.hook()).vdk_exception(
                exception=exc_value
            )
            # if at least one hook implementation returned handled, means we do not need to log the exception
            if not (True in handled):
                log.exception("Exiting with exception.")
                exit_code = 2
            else:
                exit_code = 0
        else:
            cast(JobRunHookSpecs, self._plugin_registry.hook()).finalize_job(
                context=self._job_context
            )
        cast(CoreHookSpecs, self._plugin_registry.hook()).vdk_exit(
            context=self._core_context, exit_code=exit_code
        )
        # Ensure the exception can be processed normally by calling code
        return False


class StandaloneDataJobFactory:
    @staticmethod
    def create(
        data_job_directory: pathlib.Path | None,
        name: str | None = None,
        job_args: dict | None = None,
        extra_plugins: list = [],
        template_name: str | None = None,
    ) -> IStandaloneDataJob:
        """
        Arguments:
            data_job_directory: pathlib.Path
                The source code of the data job that will be executed.
            name: Optional[str]
                The name of the job.  If omitted will be inferred from the director name.
            job_args: Optional[dict]
                Allows for users to pass arguments to data job run.
                Data Job arguments are also used for parameter substitution in queries, see execute_query docstring.
            extra_plugins: Optional[list]
                List of extra plugins to register.  Mostly useful during testing
            template_name: Optional[str]
                Template name, in case the data job is a template execution.
        """
        return StandaloneDataJob(
            data_job_directory=data_job_directory,
            name=name,
            job_args=job_args,
            extra_plugins=extra_plugins,
            template_name=template_name,
        )
