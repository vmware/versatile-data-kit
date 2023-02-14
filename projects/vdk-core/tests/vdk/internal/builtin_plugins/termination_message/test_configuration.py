# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import cast

from vdk.internal.builtin_plugins.termination_message.writer_configuration import (
    WriterConfiguration,
)
from vdk.internal.core.config import Configuration


def test_termination_message_writer_configuration():
    expected_output_file = "/dev/file.out"
    expected_writer_enabled = False

    writer_cfg = WriterConfiguration(
        cast(
            Configuration,
            dict(
                TERMINATION_MESSAGE_WRITER_ENABLED=expected_writer_enabled,
                TERMINATION_MESSAGE_WRITER_OUTPUT_FILE=expected_output_file,
            ),
        )
    )

    assert expected_output_file == writer_cfg.get_output_file()
    assert expected_writer_enabled == writer_cfg.get_writer_enabled()
