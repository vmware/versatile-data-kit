# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import tempfile

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.properties_fs.fs_properties_client import (
    FileSystemPropertiesServiceClient,
)

FS_PROPERTIES_DIRECTORY = "FS_PROPERTIES_DIRECTORY"
FS_PROPERTIES_FILENAME = "FS_PROPERTIES_FILENAME"


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for FS Properties Client with reasonable defaults
    """
    config_builder.add(
        key=FS_PROPERTIES_DIRECTORY,
        default_value=tempfile.gettempdir(),
        description="FS directory path where the JSON file is to be stored.",
    )
    config_builder.add(
        key=FS_PROPERTIES_FILENAME,
        default_value="vdk_data_jobs.json",
        description="JSON file name to be used. Placed within the FS_PROPERTIES_DIRECTORY. "
        "Supports properties storage of multiple teams and data jobs.",
    )


@hookimpl
def initialize_job(context: JobContext) -> None:
    config = context.core_context.configuration
    context.properties.set_properties_factory_method(
        "fs-properties-client",
        lambda: FileSystemPropertiesServiceClient(
            config.get_value(FS_PROPERTIES_DIRECTORY),
            config.get_value(FS_PROPERTIES_FILENAME),
        ),
    )
