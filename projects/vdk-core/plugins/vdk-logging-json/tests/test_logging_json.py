# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.vdk.logging_json import format_template


def test_json_logging():
    for handler in logging.getLogger(__name__).handlers:
        assert handler.formatter._fmt == format_template
