# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_version():
    vdk_runner = CliEntryBasedTestRunner()
    result = vdk_runner.invoke(["version"])

    cli_assert_equal(0, result)
