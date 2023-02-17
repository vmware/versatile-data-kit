# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import ConfigurationBuilder

TROUBLESHOOT_UTILITIES_TO_USE = "TROUBLESHOOT_UTILITIES_TO_USE"
TROUBLESHOOT_PORT_TO_USE = "TROUBLESHOOT_PORT_TO_USE"


def add_definitions(config_builder: ConfigurationBuilder):
    """
    Here we define what configuration settings are needed for the
    Jobs Troubleshooting plugin with reasonable defaults.
    """
    config_builder.add(
        key=TROUBLESHOOT_UTILITIES_TO_USE,
        default_value="",
        description="""
            An unordered comma-separated list of strings, indicating what
            troubleshooting utilities are to be used. E.g., "utility1,utility2".
            For full list of available utilities, check the plugin's README at:
            https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-plugins/vdk-jobs-troubleshooting/README.md
            """,
    )
    config_builder.add(
        key=TROUBLESHOOT_PORT_TO_USE,
        default_value=8783,
        description="""
        Specify an http port to be used by troubleshooting utilities (e.g.,
        utilities that rely on local http server).
        """,
    )
