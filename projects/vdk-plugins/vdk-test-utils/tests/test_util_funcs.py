# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Optional
from unittest.mock import MagicMock

import pytest
from click.testing import Result
from vdk.plugin.test_utils.util_funcs import cli_assert
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import cli_assert_output_contains


def test_cli_assert_true():
    cli_assert(True, MagicMock(Result))


def test_cli_assert_false():
    with pytest.raises(AssertionError):
        cli_assert(False, _get_result())


def test_cli_assert_exit_code():
    cli_assert_equal(0, _get_result(exit_code=0))
    cli_assert_equal(1, _get_result(exit_code=1))

    with pytest.raises(AssertionError):
        cli_assert_equal(0, _get_result(exit_code=1))


def test_cli_assert_message():
    with pytest.raises(AssertionError) as error:
        cli_assert(False, _get_result(), "my_message")
    assert "my_message" in str(error)


def test_cli_assert_contains():
    cli_assert_output_contains("foobar", _get_result(output="This is total foobar"))


def _get_result(output: Optional[str] = "", exit_code: Optional[int] = None) -> Result:
    e = Exception("foo")
    return MagicMock(
        exc_info=(type(e), e, e.__traceback__), output=output, exit_code=exit_code
    )
