# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.core.statestore import CommonStoreKeys

# the labels follow the labelling recommendations found here: http://ltsv.org/
format_template = (
    '"@timestamp":"%(asctime)s","created":"%(created)f","jobname":"{job_name}",'
    '"level":"%(levelname)s","modulename":"%(name)s","filename":"%(filename)s",'
    '"lineno":"%(lineno)s","funcname":"%(funcName)s","attemptid":"{attempt_id}","message":"%(message)s"'
)

# this class serves to escape newline characters in the log message
# as according to https://stackoverflow.com/questions/42068/how-do-i-handle-newlines-in-json
# it is currently experimental and might be removed
class RemoveNewlinesFormatter(logging.Formatter):
    def format(self, record):
        record.msg = record.msg.replace("\n", "\\n")
        return super().format(record)


@hookimpl(trylast=True)
def initialize_job(context: JobContext) -> None:
    attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
    job_name = context.name

    detailed_format = format_template.format(
        job_name=job_name, attempt_id=attempt_id
    )  # appending braces is separated due to issue with
    detailed_format = (
        "{" + detailed_format + "}"
    )  # formatting a string containing curly braces

    for handler in logging.getLogger().handlers:
        formatter = RemoveNewlinesFormatter(fmt=detailed_format)
        formatter.default_time_format = "%Y-%m-%dT%H:%M:%S"
        formatter.default_msec_format = "%s.%03dZ"

        handler.setFormatter(formatter)
