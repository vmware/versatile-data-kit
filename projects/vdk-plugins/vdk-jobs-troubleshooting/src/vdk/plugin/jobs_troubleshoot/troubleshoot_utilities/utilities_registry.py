# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import Dict
from typing import List

from vdk.internal.core.config import Configuration
from vdk.plugin.jobs_troubleshoot.api.troubleshoot_utility import ITroubleshootUtility
from vdk.plugin.jobs_troubleshoot.troubleshoot_configuration import (
    TROUBLESHOOT_UTILITIES_TO_USE,
)
from vdk.plugin.jobs_troubleshoot.troubleshoot_utilities.thread_dump import (
    ThreadDumpUtility,
)


log = logging.getLogger(__name__)


def utilities_registry(job_config: Configuration) -> Dict[str, Any]:
    """
    The troubleshooting utilities registry is where all utility objects are to
    be initialized.
    TODO: Come up with a more elegant approach to register utilities.

    :param job_config: The data job configuration.
    :return: A dictionary with all available troubleshooting utilities.
    """
    registered_utilities: Dict[str, Any] = {}
    registered_utilities["thread-dump"] = ThreadDumpUtility(
        job_configuration=job_config
    )

    return registered_utilities


def get_utilities_to_use(
    job_config: Configuration,
) -> List[ITroubleshootUtility]:
    """
    Get a list of the initialized troubleshooting utilities that are specified
    by the VDK_TROUBLESHOOT_UTILITIES_TO_USE configuration variable.
    :param job_config: Data Job configuration
    :return: A list of utility objects that are to be used.
    """
    utilities: List[ITroubleshootUtility] = []
    selected_utilities: str = job_config.get_value(TROUBLESHOOT_UTILITIES_TO_USE)
    registered_utilities: Dict = utilities_registry(job_config=job_config)

    for util in selected_utilities.split(","):
        registered_util = registered_utilities.get(util)
        if registered_util:
            utilities.append(registered_util)
        else:
            log.info(
                f"""
                Utility {util} is not in the list of available troubleshooting
                utilities.
                Available utilities: {registered_utilities.keys()}
                """
            )

    return utilities
