# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.plugin.logging_json.logging_json import EscapeNewlinesAndQuotesFormatter
from vdk.plugin.logging_json.logging_json import format_template


def test_json_logging():
    for handler in logging.getLogger(__name__).handlers:
        assert handler.formatter._fmt == format_template


def test_formatter():
    formatter = EscapeNewlinesAndQuotesFormatter(fmt="")

    log_record = logging.LogRecord(
        name="",
        level=1,
        pathname="",
        lineno=1,
        msg="test-string",
        args=(),
        exc_info=None,
    )

    assert formatter.format(log_record) == "test-string"

    log_record.msg = "test\nstring\nwith\nnewlines"
    assert formatter.format(log_record) == "test\\nstring\\nwith\\nnewlines"

    log_record.msg = 'test"string"with"double"quotes'
    assert formatter.format(log_record) == 'test\\"string\\"with\\"double\\"quotes'
