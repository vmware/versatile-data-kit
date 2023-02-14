# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from functional.run import util
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import TestPropertiesDecoratedPlugin
from vdk.plugin.test_utils.util_plugins import TestPropertiesPlugin


def test_run_properties():
    test_props = TestPropertiesPlugin()
    runner = CliEntryBasedTestRunner(test_props)
    runner.clear_default_plugins()

    test_props.properties_client.write_properties(
        "properties-job", "team", {"message": "42"}
    )

    result: Result = runner.invoke(["run", util.job_path("properties-job")])

    cli_assert_equal(0, result)
    assert test_props.properties_client.read_properties("properties-job", "team") == {
        "message": "42",
        "message_copy": "42",
    }


@mock.patch.dict(
    os.environ, {"VDK_PROPERTIES_WRITE_PREPROCESS_SEQUENCE": "test-property-decorated"}
)
def test_run_properties_write_preprocess_sequence():
    test_props = TestPropertiesPlugin()
    test_props_decorator = TestPropertiesDecoratedPlugin()
    runner = CliEntryBasedTestRunner(test_props, test_props_decorator)
    runner.clear_default_plugins()

    test_props.properties_client.write_properties(
        "properties-job", "team", {"message": "42"}
    )

    result: Result = runner.invoke(["run", util.job_path("properties-job")])

    cli_assert_equal(0, result)
    assert test_props.properties_client.read_properties("properties-job", "team") == {
        "message": "42",
        "message_copy": "42",
        "test": "True",
    }
