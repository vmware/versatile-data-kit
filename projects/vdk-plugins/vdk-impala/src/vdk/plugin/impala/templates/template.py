# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import time

from vdk.api.job_input import IJobInput
from vdk.api.job_input import ITemplate
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult

# from vacloud.vdk.connection.impl.builder import ManagedConnectionBuilder

log = logging.getLogger(__name__)


class Template(ITemplate):
    def __init__(
        self,
        git_hash: str,
        opid: str,
        managed_connection_builder,
        job_input_only_used_to_pass_to_python_scripts: IJobInput,
    ):

        self.git_hash = git_hash
        self.opid = opid
        self.managed_connection_builder = managed_connection_builder
        self.job_input_only_used_to_pass_to_python_scripts = (
            job_input_only_used_to_pass_to_python_scripts
        )

    @staticmethod
    def get_folder_where_i_am() -> str:
        my_path = os.path.realpath(__file__)
        abspath = os.path.abspath(my_path)
        folder = os.path.join(abspath, os.pardir)
        return os.path.abspath(folder)

    @staticmethod
    def get_templates_folder() -> str:
        return os.path.join(Template.get_folder_where_i_am(), "templates")

    def execute_template(
        self, template_name: str, template_args: dict
    ) -> ExecutionResult:
        log.debug(f"Execute template {template_name} {template_args}")
        start_of_execution = time.time()
        exception_message = None
        import importlib

        try:
            package_name = (
                "vacloud.vdk.templates."
                + template_name.replace("/", ".")
                + ".definition"
            )
            module = importlib.import_module(package_name)
            load = getattr(module, "load")
            load(self.job_input_only_used_to_pass_to_python_scripts, template_args)
        except Exception as e:
            exception_message = str(e)
            raise
        finally:
            data = {
                "@type": "pa__dp_template_usage",
                "template_name": template_name,
                "template_args": ",".join(
                    [str(v) for kv in template_args.items() for v in kv]
                ),
                "template_execution_time_seconds": round(
                    time.time() - start_of_execution
                ),
                "template_execution_status": "error"
                if exception_message
                else "success",
                "exception_message": exception_message if exception_message else None,
            }
            log.info(data)
            template_args_data = {"arg_" + k: v for k, v in template_args.items()}
            data.update(template_args_data)
