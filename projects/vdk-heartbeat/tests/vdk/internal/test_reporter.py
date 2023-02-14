# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from vdk.internal.heartbeat import reporter
from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.reporter import TestDecorator


@TestDecorator()
def func_pass():
    pass


@TestDecorator()
def func_fail():
    raise AttributeError("Bad attribute")


def test_pass():
    reporter._Result.test_cases.clear()
    func_pass()
    assert len(reporter._Result.test_cases) == 1
    assert reporter._Result.test_cases[0].name == "func_pass"


def test_fail():
    reporter._Result.test_cases.clear()

    with pytest.raises(AttributeError):
        func_fail()
    assert len(reporter._Result.test_cases) == 1
    assert reporter._Result.test_cases[0].name == "func_fail"
    assert len(reporter._Result.test_cases[0].failures) == 1


def test_file_generation(tmpdir):
    reporter._Result.test_cases.clear()

    func_pass()
    with pytest.raises(AttributeError):
        func_fail()

    empty_dir = tmpdir.mkdir("foo")
    test_config = MagicMock(spec=Config)
    test_junit_xml = os.path.join(empty_dir, "test-junit.xml")
    test_config.report_junit_xml_file_path = test_junit_xml

    reporter.report_results(test_config)

    file_content = Path(test_junit_xml).read_text()
    assert 'name="func_fail"' in file_content
    assert 'name="func_pass"' in file_content
