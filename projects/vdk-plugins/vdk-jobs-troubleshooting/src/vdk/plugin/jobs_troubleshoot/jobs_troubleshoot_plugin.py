# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK-JOBS-TROUBLESHOOTING plugin script.
"""
import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder

log = logging.getLogger(__name__)

TROUBLESHOOT_UTILITIES_TO_USE = "TROUBLESHOOT_UTILITIES_TO_USE"


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for the
    Jobs Troubleshooting plugin with reasonable defaults.
    """
    config_builder.add(
        key=TROUBLESHOOT_UTILITIES_TO_USE,
        default_value=None,
        description="""
        An unordered comma-separated list of strings, indicating what
        troubleshooting utilities are to be used.
        """,
    )


@hookimpl
def initialize_job(context: JobContext) -> None:
    pass
