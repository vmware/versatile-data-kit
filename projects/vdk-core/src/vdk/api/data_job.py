# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import pathlib
from abc import abstractmethod

from vdk.api.job_input import IJobInput


class IStandaloneDataJob:
    """
    A contextmanager that initialises VDK and its plugins,
    triggers plugin lifecycle hooks needed to expose an initialised IJobInput on entry
    and finalization hooks when the context is exited

    NB: The following plugin hooks are not triggered:
        * CoreHookSpecs.vdk_command_line

    Sample usage::

        with StandaloneDataJobFactory.create(datajob_directory) as job_input:
            #... use job_input object to interact with underlying data systems.
    """

    @abstractmethod
    def __init__(
        self,
        data_job_directory: pathlib.Path | None,
        name: str | None = None,
        job_args: dict | None = None,
    ):
        """
        Initialises:
            * PluginRegistry
                * load_plugins_from_setuptools_entrypoints
                * core-plugins
                * ExecutionTrackingPlugin
            * Configuration
            * CoreContext
            * StateStore
        Triggers plugin lifecycle hooks:
            * CoreHookSpecs.vdk_start.call_historic
            * CoreHookSpecs.vdk_configure
            * CoreHookSpecs.vdk_initialize

        Arguments:
            data_job_directory: Optional[pathlib.Path]
                The source code of the data job that will be executed.
            name: Optional[str]
                The name of the job.  If omitted will be inferred from the director name.
            job_args: Optional[dict]
                Allows for users to pass arguments to data job run.
                Data Job arguments are also used for parameter substitution in queries, see execute_query docstring.
        """

    @abstractmethod
    def __enter__(self) -> IJobInput:
        """
        Executes on entry to the context block:
            * Adds a noop step DataJob hook to prevent any logic being dynamically executed from step files
            * Initialises the JobContext

        And then triggers plugin lifecycle hooks:
            * initialize_job
            * run_job

        Returns:
            An initialised IJobInput object
        """
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Executes on exit of the context block

        Triggers plugin lifecycle hooks:
            * finalize_job
            * vdk_exit
        """
        pass
