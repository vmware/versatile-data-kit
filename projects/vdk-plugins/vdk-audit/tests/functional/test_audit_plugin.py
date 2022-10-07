# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from vdk.plugin.audit import audit_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


def test_audit_single_event_enabled_and_not_permitted_action():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_AUDIT_HOOK_ENABLED": "True",
            "NOT_PERMITTED_EVENTS_LIST": "os.system",
        },
    ):
        os._exit = mock.MagicMock()
        runner = CliEntryBasedTestRunner(audit_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("os-system-command-job")]
        )

        print(result.output)
        assert os._exit.called


def test_audit_single_event_with_semicolon_enabled_and_not_permitted_action():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_AUDIT_HOOK_ENABLED": "True",
            "NOT_PERMITTED_EVENTS_LIST": "os.system;",
        },
    ):
        os._exit = mock.MagicMock()
        runner = CliEntryBasedTestRunner(audit_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("os-system-command-job")]
        )

        print(result.output)
        assert os._exit.called


def test_audit_multiple_events_enabled_and_not_permitted_action():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_AUDIT_HOOK_ENABLED": "True",
            "NOT_PERMITTED_EVENTS_LIST": "os.system;os.startfile;os.symlink",
        },
    ):
        os._exit = mock.MagicMock()
        runner = CliEntryBasedTestRunner(audit_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("os-system-command-job")]
        )

        print(result.output)
        assert os._exit.called


def test_audit_multiple_events_enabled_and_permitted_action():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_AUDIT_HOOK_ENABLED": "True",
            "NOT_PERMITTED_EVENTS_LIST": "os.system;os.startfile;os.symlink",
        },
    ):
        os._exit = mock.MagicMock()
        runner = CliEntryBasedTestRunner(audit_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("os-listdir-command-job")]
        )

        print(result.output)
        cli_assert_equal(0, result)
        assert not os._exit.called


def test_audit_multiple_events_disabled_and_not_permitted_action():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_AUDIT_HOOK_ENABLED": "False",
            "NOT_PERMITTED_EVENTS_LIST": "os.system;os.startfile;os.symlink",
        },
    ):
        os._exit = mock.MagicMock()
        runner = CliEntryBasedTestRunner(audit_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("os-system-command-job")]
        )

        print(result.output)
        cli_assert_equal(0, result)
        assert not os._exit.called


def test_audit_multiple_events_disabled_and_permitted_action():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_AUDIT_HOOK_ENABLED": "False",
            "NOT_PERMITTED_EVENTS_LIST": "os.system;os.startfile;os.symlink",
        },
    ):
        os._exit = mock.MagicMock()
        runner = CliEntryBasedTestRunner(audit_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("os-listdir-command-job")]
        )

        print(result.output)
        cli_assert_equal(0, result)
        assert not os._exit.called
