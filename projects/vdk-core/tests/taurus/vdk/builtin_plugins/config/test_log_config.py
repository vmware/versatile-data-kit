# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
from unittest.mock import MagicMock

import pytest
from taurus.api.plugin.plugin_registry import IPluginRegistry
from taurus.vdk.builtin_plugins.config import vdk_config
from taurus.vdk.builtin_plugins.config.log_config import LoggingPlugin
from taurus.vdk.builtin_plugins.run.data_job import JobArguments
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.builtin_plugins.templates.template_impl import TemplatesImpl
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.core.context import CoreContext
from taurus.vdk.core.statestore import CommonStoreKeys
from taurus.vdk.core.statestore import StateStore

# TODO: we should patch logging, this changes it for all tests


@pytest.mark.parametrize(
    "log_type, level, expected_level",
    (
        ("LOCAL", "INFO", logging.INFO),
        ("REMOTE", "WARNING", logging.WARNING),
    ),
)
def test_log_plugin(log_type, level, expected_level):
    log_plugin = LoggingPlugin()

    store = StateStore()
    store.set(CommonStoreKeys.ATTEMPT_ID, "attempt_id")

    conf = (
        ConfigurationBuilder()
        .add(vdk_config.LOG_CONFIG, log_type)
        .add(vdk_config.LOG_LEVEL_VDK, level)
        .build()
    )
    core_context = CoreContext(MagicMock(spec=IPluginRegistry), conf, store)

    job_context = JobContext(
        "foo",
        pathlib.Path("foo"),
        core_context,
        JobArguments([]),
        TemplatesImpl("foo", core_context),
    )

    log_plugin.initialize_job(job_context)

    assert (
        logging.getLogger("taurus").getEffectiveLevel() == expected_level
    ), "internal vdk logs must be set according to configuration option LOG_LEVEL_VDK but are not"
