# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

TERMINATION_MESSAGE_WRITER_ENABLED = "TERMINATION_MESSAGE_WRITER_ENABLED"
TERMINATION_MESSAGE_WRITER_OUTPUT_FILE = "TERMINATION_MESSAGE_WRITER_OUTPUT_FILE"


class WriterConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def get_writer_enabled(self):
        return bool(self.__config[TERMINATION_MESSAGE_WRITER_ENABLED])

    def get_output_file(self):
        return str(self.__config[TERMINATION_MESSAGE_WRITER_OUTPUT_FILE])


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=TERMINATION_MESSAGE_WRITER_ENABLED,
        default_value=True,
        description="Set to false if you want to disable termination message writing.",
    )
    config_builder.add(
        key=TERMINATION_MESSAGE_WRITER_OUTPUT_FILE,
        default_value="/dev/termination-log",
        show_default_value=True,
        description="A file in which to write data job execution completion message.",
    )
