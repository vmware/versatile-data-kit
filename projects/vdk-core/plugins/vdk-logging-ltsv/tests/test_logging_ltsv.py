# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.plugin.logging_ltsv.logging_ltsv import format_template


def test_ltsv_logging():
    for handler in logging.getLogger(__name__).handlers:
        assert handler.formatter._fmt == format_template
