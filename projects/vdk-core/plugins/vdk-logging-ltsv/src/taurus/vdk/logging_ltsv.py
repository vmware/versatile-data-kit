# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.core.statestore import CommonStoreKeys

# the labels follow the labelling recommendations found here: http://ltsv.org/
format_template = (
    "@timestamp:%(asctime)s\tcreated:%(created)f\tjobname:{}\tlevel:%(levelname)s\tmodulename:%(name)s"
    "\tfilename:%(filename)s\tlineno:%(lineno)s\tfuncname:%(funcName)s\tattemptid:{}\tmessage:%(message)s"
)


@hookimpl(trylast=True)
def initialize_job(context: JobContext) -> None:
    attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
    job_name = context.name

    detailed_format = format_template.format(job_name, attempt_id)

    for handler in logging.getLogger().handlers:
        handler.setFormatter(logging.Formatter(detailed_format))
