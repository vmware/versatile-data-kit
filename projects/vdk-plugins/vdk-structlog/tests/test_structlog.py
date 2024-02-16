# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import re
import socket
import threading
from unittest import mock

import pytest
from click.testing import Result
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import VdkConfigurationError
from vdk.internal.core.statestore import StateStore
from vdk.plugin.structlog import structlog_plugin
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_ENABLED
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_HOST
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_PORT
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_PROTOCOL
from vdk.plugin.structlog.constants import JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT
from vdk.plugin.structlog.constants import STRUCTLOG_CONFIG_PRESET
from vdk.plugin.structlog.constants import STRUCTLOG_CONSOLE_LOG_PATTERN
from vdk.plugin.structlog.constants import STRUCTLOG_FORMAT_INIT_LOGS
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_DEFAULT
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_KEY
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_POSSIBLE_VALUES
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_METADATA_ALL_KEYS
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_METADATA_KEY
from vdk.plugin.structlog.constants import STRUCTLOG_USE_STRUCTLOG
from vdk.plugin.structlog.constants import SYSLOG_ENABLED_KEY
from vdk.plugin.structlog.constants import SYSLOG_HOST_KEY
from vdk.plugin.structlog.constants import SYSLOG_PORT_KEY
from vdk.plugin.structlog.constants import SYSLOG_PROTOCOL_KEY
from vdk.plugin.structlog.log_level_utils import parse_log_level_module
from vdk.plugin.structlog.structlog_plugin import StructlogPlugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

JOB_NAME = "job-with-bound-logger"
BOUND_TEST_KEY = "bound_test_key"
BOUND_TEST_VALUE = "bound_test_value"
EXTRA_TEST_KEY = "extra_test_key"
EXTRA_TEST_VALUE = "extra_test_value"
EXCLUDED_BOUND_TEST_KEY = "excluded_bound_test_key"
EXCLUDED_BOUND_TEST_VALUE = "excluded_bound_test_value"

# TODO: add vdk_step_name
# TODO: add attempt_id
STOCK_FIELDS = [
    "timestamp",
    "level",
    "file_name",
    "line_number",
    "function_name",
    "vdk_job_name",
    # TODO: Figure out how to distinguish step name from file name
    #    "vdk_step_name",
    "vdk_step_type",
]
STOCK_FIELD_REPRESENTATIONS = {
    "console": {
        "timestamp": r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}",
        "level": r"\[INFO ]",
        "file_name": r"10_dummy\.py",
        "line_number": r"\s:[0-9]+",
        "function_name": "run",
        "vdk_job_name": JOB_NAME,
        "vdk_step_name": r"10_dummy\.py",
        "vdk_step_type": r"python",
    },
    "ltsv": {
        "timestamp": r"timestamp:\d+\.\d+",
        "level": r"level:INFO",
        "file_name": r"file_name:10_dummy\.py",
        "line_number": "line_number:[0-9]+",
        "function_name": "function_name:run",
        "vdk_job_name": f"vdk_job_name:{JOB_NAME}",
        "vdk_step_name": r"vdk_step_name:10_dummy\.py",
        "vdk_step_type": "vdk_step_type:python",
    },
    "json": {
        "timestamp": r'"timestamp": \d+\.\d+',
        "level": '"level": "INFO"',
        "file_name": '"filename": "10_dummy.py"',
        "line_number": '"lineno": [0-9]+',
        "function_name": '"funcName": "run"',
        "vdk_job_name": f'"vdk_job_name": "{JOB_NAME}"',
        "vdk_step_name": '"vdk_step_name": "10_dummy.py"',
        "vdk_step_type": '"vdk_step_type": "python"',
    },
}


@pytest.mark.parametrize("log_format", ["console", "ltsv", "json"])
def test_structlog(log_format):
    with mock.patch.dict(
        os.environ,
        {
            "VDK_STRUCTLOG_METADATA": f"timestamp,level,file_name,line_number,vdk_job_name,{BOUND_TEST_KEY},{EXTRA_TEST_KEY}",
            "VDK_STRUCTLOG_FORMAT": log_format,
            "LOG_LEVEL_MODULE": "test_structlog=WARNING",
        },
    ):
        logs = _run_job_and_get_logs()

        log_with_no_bound_context = _get_log_containing_s(
            logs, "Log statement with no bound context"
        )
        log_with_bound_context = _get_log_containing_s(
            logs, "Log statement with bound context"
        )
        log_with_bound_and_extra_context = _get_log_containing_s(
            logs, "Log statement with bound context and extra context"
        )

        # due to the log_level_module config specified in the config.ini of the test job
        # the 'This log statement should not appear' log should not appear in the output logs
        assert (
            _get_log_containing_s(logs, "This log statement should not appear") is None
        )

        _assert_cases(
            log_with_no_bound_context,
            log_with_bound_context,
            log_with_bound_and_extra_context,
        )


def test_structlog_syslog():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_STRUCTLOG_FORMAT": "console",
            "VDK_STRUCTLOG_CONSOLE_CUSTOM_FORMAT": "%(asctime)s [VDK] %(vdk_job_name)s [%(levelname)-5.5s] %(name)-30.30s "
            "%(filename)20.20s:%(lineno)-4.4s %(funcName)-16.16s[id:%("
            "attempt_id)s]- %(message)s",
            "LOG_LEVEL_MODULE": "test_structlog=WARNING",
            "VDK_SYSLOG_HOST": "127.0.0.1",
            "VDK_SYSLOG_PORT": "32123",
            "VDK_SYSLOG_PROTOCOL": "UDP",
            "VDK_SYSLOG_ENABLED": "True",
        },
    ):
        syslog_out = []

        def start_syslog_server(host, port):
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind((host, port))
            print(f"Syslog server listening on {host}:{port}")

            while True:
                data, addr = server_socket.recvfrom(1024)
                syslog_out.append(f"{data.decode('utf-8')}")

        server = threading.Thread(
            target=start_syslog_server, args=("127.0.0.1", 32123), daemon=True
        )
        server.start()

        _run_job_and_get_logs()

        assert syslog_out

        # assert log entries are formatted using the hardcoded formatter
        for log in syslog_out:
            assert re.search("\\[id:.*\\]", log)


@pytest.mark.parametrize("log_format", ["console", "ltsv", "json"])
def test_stock_fields_removal(log_format):
    stock_field_reps = STOCK_FIELD_REPRESENTATIONS[log_format]

    for removed_field in STOCK_FIELDS:
        shown_fields = [field for field in STOCK_FIELDS if field != removed_field]
        vdk_logging_metadata = ",".join(shown_fields) + ",bound_test_key,extra_test_key"

        with mock.patch.dict(
            os.environ,
            {
                "VDK_STRUCTLOG_METADATA": vdk_logging_metadata,
                "VDK_STRUCTLOG_FORMAT": log_format,
            },
        ):
            logs = _run_job_and_get_logs()

            test_log = _get_log_containing_s(
                logs, "Log statement with bound context and extra context"
            )

            # check that the removed_field is not shown in the log
            assert re.search(stock_field_reps[removed_field], test_log) is None

            # check the rest are shown
            for shown_field in shown_fields:
                assert re.search(stock_field_reps[shown_field], test_log) is not None


@pytest.mark.parametrize("log_format", ["console"])
def test_custom_format_applied(log_format):
    custom_format_string = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

    with mock.patch.dict(
        os.environ,
        {
            "VDK_STRUCTLOG_FORMAT": log_format,
            "VDK_STRUCTLOG_CONSOLE_CUSTOM_FORMAT": custom_format_string,
        },
    ):
        logs = _run_job_and_get_logs()

        for log in logs:
            if "Log statement with no bound context" in log:
                assert _matches_custom_format(log)
                break
        else:
            pytest.fail("Log statement with no bound context not found in logs")


@pytest.mark.parametrize("log_format", ["json", "ltsv"])
def test_custom_format_not_applied_for_non_console_formats(log_format):
    custom_format_string = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

    with mock.patch.dict(
        os.environ,
        {
            "VDK_STRUCTLOG_METADATA": "timestamp,level,file_name,vdk_job_name",
            "VDK_STRUCTLOG_FORMAT": log_format,
            "VDK_STRUCTLOG_CUSTOM_CONSOLE_FORMAT": custom_format_string,
        },
    ):
        logs = _run_job_and_get_logs()

        for log in logs:
            if "Log statement with no bound context" in log:
                assert not _matches_custom_format(
                    log
                ), f"Custom format was incorrectly applied for {log_format} format. Log: {log}"
                break
        else:
            pytest.fail("Log statement with no bound context not found in logs")


def test_structlog_custom_format_vdk_fields():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_STRUCTLOG_FORMAT": "console",
            "VDK_STRUCTLOG_CONSOLE_CUSTOM_FORMAT": "job_name: %(vdk_job_name)s step_name: %(vdk_step_name)s step_type: %(vdk_step_type)s %(message)s",
            "VDK_STRUCTLOG_FORMAT_INIT_LOGS": "True",
            "VDK_LOG_LEVEL_MODULE": "test_structlog=WARNING",
        },
    ):
        expected = [
            "job_name: job-with-bound-logger step_name: 10_dummy.py step_type: python Entering "
            "10_dummy.py#run(...) ...",
            "job_name: job-with-bound-logger step_name: 10_dummy.py step_type: "
            "python Log statement with no bound context",
            "job_name: "
            "job-with-bound-logger "
            "step_name: 10_dummy.py "
            "step_type: python Log "
            "statement with bound "
            "context",
            "job_name: "
            "job-with"
            "-bound"
            "-logger "
            "step_name: "
            "10_dummy.py "
            "step_type: "
            "python Log "
            "statement "
            "with bound "
            "context and "
            "extra "
            "context",
            "job_name: job-with-bound-logger step_name: 10_dummy.py step_type: python Exiting  "
            "10_dummy.py#run(...) SUCCESS",
            "job_name: job-with-bound-logger step_name:  step_type:  Job "
            "execution result: SUCCESS",
            "Step results:",
            "10_dummy.py - " "SUCCESS",
            "",
            "",
        ]
        logs = _run_job_and_get_logs()
        assert logs
        assert len(logs) == len(expected)
        for i, log in enumerate(logs):
            assert log == expected[i]


@pytest.mark.parametrize("log_format", ["console", "json", "ltsv"])
def test_step_name_step_type(log_format):
    stock_field_reps = STOCK_FIELD_REPRESENTATIONS[log_format]
    with mock.patch.dict(
        os.environ,
        {
            "VDK_STRUCTLOG_METADATA": "vdk_step_type,vdk_step_name",
            "VDK_STRUCTLOG_FORMAT": log_format,
        },
    ):
        logs = _run_job_and_get_logs()
        test_log = _get_log_containing_s(logs, "Log statement with no bound context")
        assert re.search(stock_field_reps["vdk_step_name"], test_log) is not None
        assert re.search(stock_field_reps["vdk_step_type"], test_log) is not None

    with mock.patch.dict(
        os.environ,
        {
            "VDK_STRUCTLOG_METADATA": "vdk_step_name",
            "VDK_STRUCTLOG_FORMAT": log_format,
        },
    ):
        logs = _run_job_and_get_logs()
        test_log = _get_log_containing_s(logs, "Log statement with no bound context")
        assert re.search(stock_field_reps["vdk_step_name"], test_log) is not None
        assert re.search(stock_field_reps["vdk_step_type"], test_log) is None

    with mock.patch.dict(
        os.environ,
        {
            "VDK_STRUCTLOG_METADATA": "vdk_step_type",
            "VDK_STRUCTLOG_FORMAT": log_format,
        },
    ):
        logs = _run_job_and_get_logs()
        test_log = _get_log_containing_s(logs, "Log statement with no bound context")
        assert re.search(stock_field_reps["vdk_step_name"], test_log) is None
        assert re.search(stock_field_reps["vdk_step_type"], test_log) is not None


def _matches_custom_format(log):
    pattern = re.compile(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \S{1,12} \S{1,8} .+"
    )
    return bool(pattern.search(log))


@pytest.mark.parametrize(
    "log_type, vdk_level, expected_vdk_level",
    (
        ("LOCAL", "INFO", logging.INFO),
        ("REMOTE", "WARNING", logging.WARNING),
        ("LOCAL", None, logging.DEBUG),  # if not set default to root log level
    ),
)
def test_log_plugin_structlog(log_type, vdk_level, expected_vdk_level):
    logging.getLogger().setLevel(logging.DEBUG)  # root level
    logging.getLogger("vdk").setLevel(logging.NOTSET)  # reset vdk log level

    log_plugin = StructlogPlugin()

    metadata_keys = "timestamp,level,file_name,line_number,vdk_job_name,bound_test_key,extra_test_key"
    logging_format = "console"

    store = StateStore()
    conf = (
        ConfigurationBuilder()
        .add(vdk_config.LOG_CONFIG, log_type)
        .add(vdk_config.LOG_LEVEL_VDK, vdk_level)
        .add(STRUCTLOG_LOGGING_METADATA_KEY, metadata_keys)
        .add(STRUCTLOG_LOGGING_FORMAT_KEY, logging_format)
        .add(STRUCTLOG_CONFIG_PRESET, "LOCAL")
        .add(STRUCTLOG_FORMAT_INIT_LOGS, False)
        .set_value(STRUCTLOG_FORMAT_INIT_LOGS, True)
        .build()
    )
    core_context = CoreContext(mock.MagicMock(spec=IPluginRegistry), conf, store)

    log_plugin.vdk_initialize(core_context)

    assert logging.getLogger("vdk").getEffectiveLevel() == expected_vdk_level


def test_parse_log_level_module_structlog():
    assert parse_log_level_module("") == {}
    assert parse_log_level_module("a.b.c=INFO") == {"a.b.c": {"level": "INFO"}}
    assert parse_log_level_module("a.b.c=info") == {"a.b.c": {"level": "INFO"}}
    assert parse_log_level_module("a.b.c=INFO;x.y=WARN") == {
        "a.b.c": {"level": "INFO"},
        "x.y": {"level": "WARN"},
    }


def test_parse_log_level_module_error_cases_structlog():
    with pytest.raises(VdkConfigurationError):
        parse_log_level_module("a.b.c=NOSUCH")

    with pytest.raises(VdkConfigurationError):
        parse_log_level_module("bad_separator_not_semi_colon=DEBUG,second_module=INFO")


def test_log_plugin_exception_structlog():
    with mock.patch(
        "vdk.plugin.structlog.structlog_plugin.create_formatter"
    ) as mocked_create_formatter:
        mocked_create_formatter.side_effect = Exception("foo")

        log_plugin = StructlogPlugin()

        # Mock configuration since we won't be needing any.

        store = StateStore()
        conf = (
            ConfigurationBuilder()
            .add(STRUCTLOG_CONFIG_PRESET, "LOCAL")
            .add(STRUCTLOG_FORMAT_INIT_LOGS, False)
            .set_value(STRUCTLOG_FORMAT_INIT_LOGS, True)
            .build()
        )
        core_context = CoreContext(mock.MagicMock(spec=IPluginRegistry), conf, store)
        with pytest.raises(Exception) as exc_info:
            log_plugin.vdk_initialize(core_context)
        assert str(exc_info.value) == "foo", "Unexpected exception message"


def test_structlog_property_override_presets():
    log_plugin = StructlogPlugin()

    store = StateStore()
    conf = (
        ConfigurationBuilder()
        .add(
            key=STRUCTLOG_LOGGING_METADATA_KEY,
            default_value=",".join(
                list(JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT.keys())
            ),
            description=(
                f"Possible values: {STRUCTLOG_LOGGING_METADATA_ALL_KEYS}"
                "User-defined key-value pairs added to the logger's context will be displayed after the metadata, "
                "but before the message"
                "Keys for user-defined key-value pairs have to be added in this config option for the values to be "
                "displayed in the metadata"
            ),
        )
        .add(
            key=STRUCTLOG_CONSOLE_LOG_PATTERN,
            default_value="",
            description="Custom format string for console logging. Leave empty for default format.",
        )
        .add(
            key=STRUCTLOG_LOGGING_FORMAT_KEY,
            default_value=STRUCTLOG_LOGGING_FORMAT_DEFAULT,
            description=(
                f"Controls the logging output format. Possible values: {STRUCTLOG_LOGGING_FORMAT_POSSIBLE_VALUES}"
            ),
        )
        .add(
            key=SYSLOG_HOST_KEY,
            default_value=DEFAULT_SYSLOG_HOST,
            description="Hostname of the Syslog server.",
        )
        .add(
            key=SYSLOG_PORT_KEY,
            default_value=DEFAULT_SYSLOG_PORT,
            description="Port of the Syslog server.",
        )
        .add(
            key=SYSLOG_PROTOCOL_KEY,
            default_value=DEFAULT_SYSLOG_PROTOCOL,
            description="Syslog protocol (UDP or TCP).",
        )
        .add(
            key=SYSLOG_ENABLED_KEY,
            default_value=DEFAULT_SYSLOG_ENABLED,
            description="Enable Syslog logging (True or False).",
        )
        .add(
            key=STRUCTLOG_CONFIG_PRESET,
            default_value="LOCAL",
            description="Choose configuration preset. Any config options set together with the preset will override "
            "the preset options. Available presets: LOCAL, CLOUD",
        )
        .add(
            key=STRUCTLOG_USE_STRUCTLOG,
            default_value=True,
            description="Use the structlog logging config instead of using the one in vdk-core",
        )
        .set_value(STRUCTLOG_CONFIG_PRESET, "CLOUD")
        .set_value(STRUCTLOG_USE_STRUCTLOG, False)
        .set_value(STRUCTLOG_LOGGING_METADATA_KEY, "timestamp,level")
        .set_value(STRUCTLOG_LOGGING_FORMAT_KEY, "json")
        .set_value(STRUCTLOG_CONSOLE_LOG_PATTERN, "")
        .set_value(SYSLOG_HOST_KEY, "127.0.0.1")
        .set_value(SYSLOG_PORT_KEY, 8888)
        .set_value(SYSLOG_PROTOCOL_KEY, "TCP")
        .set_value(SYSLOG_ENABLED_KEY, False)
        .set_value(vdk_config.LOG_LEVEL_MODULE, "test_structlog=DEBUG")
        .set_value(vdk_config.LOG_LEVEL_VDK, "DEBUG")
        .build()
    )
    core_context = CoreContext(mock.MagicMock(spec=IPluginRegistry), conf, store)
    log_plugin.vdk_initialize(core_context)
    conf = log_plugin._config

    assert conf.get_structlog_config_preset() == "CLOUD"
    assert conf.get_use_structlog() is False
    assert conf.get_structlog_logging_metadata() == "timestamp,level"
    assert conf.get_structlog_logging_format() == "json"
    assert conf.get_structlog_console_log_pattern() == ""
    assert conf.get_syslog_host() == "127.0.0.1"
    assert conf.get_syslog_port() == 8888
    assert conf.get_syslog_protocol() == "TCP"
    assert conf.get_syslog_enabled() is False
    assert conf.get_log_level_module() == "test_structlog=DEBUG"
    assert conf.get_log_level_vdk() == "DEBUG"


def _run_job_and_get_logs():
    """
    Runs the necessary job and returns the output logs.

    :return: Job logs
    """
    runner = CliEntryBasedTestRunner(structlog_plugin)

    result: Result = runner.invoke(
        [
            "run",
            "--arguments",
            _get_job_arguments(),
            jobs_path_from_caller_directory("job-with-bound-logger"),
        ]
    )
    cli_assert_equal(0, result)
    return result.output.split("\n")


def _get_log_containing_s(logs, s):
    """
    Given a list of logs and a string, returns the first log which contains the string
    :param logs:
    :param s:
    :return:
    """
    necessary_log = [x for x in logs if s in x]
    if len(necessary_log) == 0:
        return None
    else:
        return necessary_log[0]


def _assert_cases(
    log_with_no_bound_context, log_with_bound_context, log_with_bound_and_extra_context
):
    # check for job name in logs
    assert (
        (JOB_NAME in log_with_no_bound_context)
        and (JOB_NAME in log_with_bound_context)
        and (JOB_NAME in log_with_bound_and_extra_context)
    )

    # check that bound logger can bind context but that bound context does not appear in the rest of logging
    assert (BOUND_TEST_VALUE in log_with_bound_context) and (
        BOUND_TEST_VALUE not in log_with_no_bound_context
    )

    # check extra bound context does not appear if not set in the logging_metadata config variable
    assert EXTRA_TEST_VALUE not in log_with_bound_context

    # check for both the bound and the extra context in bound log statements which include extra context
    assert (EXTRA_TEST_VALUE in log_with_bound_and_extra_context) and (
        BOUND_TEST_VALUE in log_with_bound_and_extra_context
    )

    # check that one of the bound values does not appear in the logs since we've not configured it to appear
    assert (EXCLUDED_BOUND_TEST_VALUE not in log_with_bound_context) and (
        EXCLUDED_BOUND_TEST_VALUE not in log_with_bound_and_extra_context
    )

    # check the log level and job name appear in the logs (so we can compare to when we exclude them below)
    assert ("INFO" in log_with_no_bound_context) and (
        JOB_NAME in log_with_no_bound_context
    )


def _get_job_arguments():
    bound_fields = f'{{"{BOUND_TEST_KEY}": "{BOUND_TEST_VALUE}", "{EXCLUDED_BOUND_TEST_KEY}": "{EXCLUDED_BOUND_TEST_VALUE}"}}'
    extra_fields = f'{{"{EXTRA_TEST_KEY}": "{EXTRA_TEST_VALUE}"}}'

    return f'{{"bound_fields": {bound_fields}, "extra_fields": {extra_fields}}}'
