# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from functional.run import util
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import TestSecretsDecoratedPlugin
from vdk.plugin.test_utils.util_plugins import TestSecretsPlugin


def test_run_secrets():
    test_secrets = TestSecretsPlugin()
    runner = CliEntryBasedTestRunner(test_secrets)
    runner.clear_default_plugins()

    test_secrets.secrets_client.write_secrets("secrets-job", "team", {"message": "42"})

    result: Result = runner.invoke(["run", util.job_path("secrets-job")])

    cli_assert_equal(0, result)
    assert test_secrets.secrets_client.read_secrets("secrets-job", "team") == {
        "message": "42",
        "message_copy": "42",
    }


@mock.patch.dict(
    os.environ, {"VDK_SECRETS_WRITE_PREPROCESS_SEQUENCE": "test-secret-decorated"}
)
def test_run_secrets_write_preprocess_sequence():
    test_secrets = TestSecretsPlugin()
    test_secrets_decorator = TestSecretsDecoratedPlugin()
    runner = CliEntryBasedTestRunner(test_secrets, test_secrets_decorator)
    runner.clear_default_plugins()

    test_secrets.secrets_client.write_secrets("secrets-job", "team", {"message": "42"})

    result: Result = runner.invoke(["run", util.job_path("secrets-job")])

    cli_assert_equal(0, result)
    assert test_secrets.secrets_client.read_secrets("secrets-job", "team") == {
        "message": "42",
        "message_copy": "42",
        "test": "True",
    }
