# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from typing import List

from ecs_logging import StdlibFormatter
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.statestore import CommonStoreKeys


class EcsJsonFormatter(StdlibFormatter):
    def __init__(self, job_name, attempt_id):
        super().__init__()
        self.__job_name = job_name
        self.__attempt_id = attempt_id

    def format(self, record):
        result = self.format_to_ecs(record)

        # fix the names of some fields and then remove their duplicates
        result["level"] = result["log"]["level"].upper()
        result["lineno"] = result["log"]["origin"]["file"]["line"]
        result["filename"] = result["log"]["origin"]["file"]["name"]
        result["modulename"] = result["log"]["logger"]
        result["funcname"] = result["log"]["origin"]["function"]
        if "error" in result:
            result["error.message"] = result["error"]["message"]
            result["error.stack_trace"] = result["error"]["stack_trace"]
            result["error.type"] = result["error"]["type"]

            result.pop("error")

        result.pop("log")
        result.pop("process")
        result.pop("ecs")

        # bind extra fields
        result["jobname"] = self.__job_name
        result["attemptid"] = self.__attempt_id

        return json.dumps(result)


@hookimpl(tryfirst=True)
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    for handler in logging.getLogger().handlers:
        handler.setFormatter(
            EcsJsonFormatter(
                job_name="",
                attempt_id="",
            )
        )


@hookimpl(trylast=True)
def initialize_job(context: JobContext) -> None:
    attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
    job_name = context.name

    for handler in logging.getLogger().handlers:
        handler.setFormatter(EcsJsonFormatter(job_name=job_name, attempt_id=attempt_id))
