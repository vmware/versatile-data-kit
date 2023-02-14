# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
from typing import List

from ecs_logging import StdlibFormatter
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.statestore import CommonStoreKeys

LOGGING_FORMAT = "LOGGING_FORMAT"

# the labels follow the labelling recommendations found here: http://ltsv.org/
ltsv_format_template = (
    "@timestamp:%(asctime)s\tcreated:%(created)f\tjobname:{}\tlevel:%(levelname)s\tmodulename:%(name)s"
    "\tfilename:%(filename)s\tlineno:%(lineno)s\tfuncname:%(funcName)s\tattemptid:{}\tmessage:%(message)s"
)


class EcsJsonFormatter(StdlibFormatter):
    def __init__(self, job_name: str, attempt_id: str, op_id: str):
        super().__init__()
        self.__job_name = job_name
        self.__attempt_id = attempt_id
        self.__op_id = op_id

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
        result["opid"] = self.__op_id

        return json.dumps(result)


def set_json_formatter(job_name, attempt_id, op_id):
    for handler in logging.getLogger().handlers:
        handler.setFormatter(
            EcsJsonFormatter(
                job_name=job_name,
                attempt_id=attempt_id,
                op_id=op_id,
            )
        )


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=LOGGING_FORMAT,
        default_value="TEXT",
        description="The format in which to structure VDK logs. Possible values are TEXT, JSON or LTSV.",
    )


@hookimpl(tryfirst=True)
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    logging_format = os.getenv("VDK_LOGGING_FORMAT")
    if (
        logging_format == "JSON"
    ):  # workaround: config isn't initialized yet but logs are being printed
        set_json_formatter("", "", "")
    elif logging_format == "LTSV":
        for handler in logging.getLogger().handlers:
            handler.setFormatter(logging.Formatter(ltsv_format_template.format("", "")))


@hookimpl(trylast=True)
def initialize_job(context: JobContext) -> None:
    logging_format = context.core_context.configuration.get_value(LOGGING_FORMAT)
    if logging_format == "JSON":
        attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
        op_id = context.core_context.state.get(CommonStoreKeys.OP_ID)
        job_name = context.name

        set_json_formatter(job_name, attempt_id, op_id)
    elif logging_format == "LTSV":
        attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
        job_name = context.name

        detailed_format = ltsv_format_template.format(job_name, attempt_id)

        for handler in logging.getLogger().handlers:
            handler.setFormatter(logging.Formatter(detailed_format))
