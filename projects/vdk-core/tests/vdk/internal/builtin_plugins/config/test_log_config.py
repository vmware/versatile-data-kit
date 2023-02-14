# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
from unittest import mock
from unittest.mock import patch

import pytest
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.config import log_config
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.builtin_plugins.config.log_config import _parse_log_level_module
from vdk.internal.builtin_plugins.config.log_config import configure_loggers
from vdk.internal.builtin_plugins.config.log_config import LoggingPlugin
from vdk.internal.builtin_plugins.config.log_config import SYSLOG_ENABLED
from vdk.internal.builtin_plugins.config.log_config import SYSLOG_PORT
from vdk.internal.builtin_plugins.config.log_config import SYSLOG_SOCK_TYPE
from vdk.internal.builtin_plugins.config.log_config import SYSLOG_URL
from vdk.internal.builtin_plugins.run.data_job import JobArguments
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.templates.template_impl import TemplatesImpl
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import VdkConfigurationError
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.internal.core.statestore import StateStore

# TODO: we should patch logging, this changes it for all tests


@pytest.mark.parametrize(
    "log_type, vdk_level, expected_vdk_level",
    (
        ("LOCAL", "INFO", logging.INFO),
        ("REMOTE", "WARNING", logging.WARNING),
        ("LOCAL", None, logging.DEBUG),  # if not set default to root log level
    ),
)
def test_log_plugin(log_type, vdk_level, expected_vdk_level):
    try:
        with mock.patch("socket.socket.connect"):
            logging.getLogger().setLevel(logging.DEBUG)  # root level
            logging.getLogger("vdk").setLevel(logging.NOTSET)  # reset vdk log level

            log_plugin = LoggingPlugin()

            store = StateStore()
            store.set(CommonStoreKeys.ATTEMPT_ID, "attempt_id")

            conf = (
                ConfigurationBuilder()
                .add(vdk_config.LOG_CONFIG, log_type)
                .add(vdk_config.LOG_LEVEL_VDK, vdk_level)
                .add(SYSLOG_URL, "localhost")
                .add(SYSLOG_PORT, 514)
                .add(SYSLOG_ENABLED, True)
                .add(SYSLOG_SOCK_TYPE, "UDP")
                .build()
            )
            core_context = CoreContext(
                mock.MagicMock(spec=IPluginRegistry), conf, store
            )

            job_context = JobContext(
                "foo",
                pathlib.Path("foo"),
                core_context,
                JobArguments([]),
                TemplatesImpl("foo", core_context),
            )

            log_plugin.initialize_job(job_context)

            assert (
                logging.getLogger("vdk").getEffectiveLevel() == expected_vdk_level
            ), "internal vdk logs must be set according to configuration option LOG_LEVEL_VDK but are not"
    finally:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("vdk").setLevel(logging.INFO)


def test_parse_log_level_module():
    assert _parse_log_level_module("") == {}
    assert _parse_log_level_module("a.b.c=INFO") == {"a.b.c": {"level": "INFO"}}
    assert _parse_log_level_module("a.b.c=info") == {"a.b.c": {"level": "INFO"}}
    assert _parse_log_level_module("a.b.c=INFO;x.y=WARN") == {
        "a.b.c": {"level": "INFO"},
        "x.y": {"level": "WARN"},
    }


def test_parse_log_level_module_error_cases():
    with pytest.raises(VdkConfigurationError):
        _parse_log_level_module("a.b.c=NOSUCH")

    with pytest.raises(VdkConfigurationError):
        _parse_log_level_module("bad_separator_not_semi_colon=DEBUG,second_module=INFO")


def test_configure_logger():
    with patch("logging.config.dictConfig") as mock_dict_config:
        with patch.object(log_config, "_set_already_configured"):
            configure_loggers(
                job_name="job-name",
                attempt_id="attempt-id",
                log_level_module="a.b.c=INFO;foo.bar=ERROR",
            )
            configured_loggers = mock_dict_config.call_args[0][0]["loggers"]
            assert configured_loggers["a.b.c"]["level"] == "INFO"
            assert configured_loggers["foo.bar"]["level"] == "ERROR"
