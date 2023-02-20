# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.plugin.logging_format.logging_format import EcsJsonFormatter


def test_formatter():
    formatter = EcsJsonFormatter(job_name="", attempt_id="", op_id="")

    log_record = logging.LogRecord(
        name="",
        level=1,
        pathname="",
        lineno=1,
        msg="test-string",
        args=(),
        exc_info=None,
        func="",
    )

    # we slice the result at the 43rd character to skip the timestamp since it'll be different every time
    result = formatter.format(log_record)
    assert result[43:] == (
        '"message": "test-string", "level": "LEVEL 1", '
        '"lineno": 1, "filename": "", "modulename": "", '
        '"funcname": "", "jobname": "", "attemptid": "", "opid": ""}'
    )

    log_record.msg = "test\nstring\nwith\nnewlines"
    result = formatter.format(log_record)
    assert result[43:] == (
        '"message": "test\\nstring\\nwith\\nnewlines", '
        '"level": "LEVEL 1", "lineno": 1, "filename": "", '
        '"modulename": "", "funcname": "", "jobname": "", "attemptid": "", "opid": ""}'
    )

    log_record.msg = 'test"string"with"double"quotes'
    result = formatter.format(log_record)
    assert result[43:] == (
        '"message": "test\\"string\\"with\\"double\\"quotes", '
        '"level": "LEVEL 1", "lineno": 1, "filename": "", '
        '"modulename": "", "funcname": "", "jobname": "", "attemptid": "", "opid": ""}'
    )
