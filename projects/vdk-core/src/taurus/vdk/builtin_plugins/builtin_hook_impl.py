# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import time
import uuid
from datetime import datetime
from typing import List

import click
from taurus.api.plugin.core_hook_spec import JobRunHookSpecs
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk import vdk_build_info
from taurus.vdk.builtin_plugins.config.config_help import ConfigHelpPlugin
from taurus.vdk.builtin_plugins.config.log_config import LoggingPlugin
from taurus.vdk.builtin_plugins.config.vdk_config import CoreConfigDefinitionPlugin
from taurus.vdk.builtin_plugins.config.vdk_config import EnvironmentVarsConfigPlugin
from taurus.vdk.builtin_plugins.config.vdk_config import JobConfigIniPlugin
from taurus.vdk.builtin_plugins.debug.debug import DebugPlugins
from taurus.vdk.builtin_plugins.ingestion.ingester_configuration_plugin import (
    IngesterConfigurationPlugin,
)
from taurus.vdk.builtin_plugins.job_properties.properties_api_plugin import (
    PropertiesApiPlugin,
)
from taurus.vdk.builtin_plugins.notification.notification import NotificationPlugin
from taurus.vdk.builtin_plugins.version.new_version_check_plugin import (
    NewVersionCheckPlugin,
)
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.core.context import CoreContext
from taurus.vdk.core.statestore import CommonStoreKeys
from taurus.vdk.plugin.plugin import PluginRegistry

log = logging.getLogger(__name__)


class RuntimeStateInitializePlugin:
    """
    Initialize in the StateStore common runtime attributes
    """

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        """
        Some job attributes like op_id can be passed externally as configuration.
        """
        config_builder.add(CommonStoreKeys.OP_ID.key, None)
        config_builder.add(CommonStoreKeys.EXECUTION_ID.key, None)
        config_builder.add(CommonStoreKeys.ATTEMPT_ID.key, None)

    @hookimpl(tryfirst=True)
    def vdk_initialize(self, context: CoreContext) -> None:
        """
        Setup common state attributes of the app (CommonStoreKeys).

        Configuration can override an attempt/op/execution id.

        Otherwise each is auto-generated in format:
        * Attempt id format is "execution_id-random_suffix"
        * Execution id format is "op_id-random_suffix"
        * Op Id is random string.
        """
        op_id = context.configuration.get_value(CommonStoreKeys.OP_ID.key)
        execution_id = context.configuration.get_value(CommonStoreKeys.EXECUTION_ID.key)
        attempt_id = context.configuration.get_value(CommonStoreKeys.ATTEMPT_ID.key)

        if not op_id:
            op_id = str(int(time.time()))

        if not execution_id:
            execution_id = f"{op_id}-{str(uuid.uuid4())[:6]}"

        if not attempt_id:
            attempt_id = f"{execution_id}-{str(uuid.uuid4())[:6]}"

        context.state.set(CommonStoreKeys.OP_ID, op_id)
        context.state.set(CommonStoreKeys.EXECUTION_ID, execution_id)
        context.state.set(CommonStoreKeys.ATTEMPT_ID, attempt_id)

        context.state.set(CommonStoreKeys.VDK_VERSION, vdk_build_info.RELEASE_VERSION)
        context.state.set(CommonStoreKeys.START_TIME, datetime.utcnow())


@hookimpl
def vdk_start(plugin_registry: PluginRegistry, command_line_args: List) -> None:
    """
    Load all default (builtin) vdk plugins
    """
    log.info("Load default (builtin) vdk plugins.")
    plugin_registry.load_plugin_with_hooks_impl(DebugPlugins())
    plugin_registry.load_plugin_with_hooks_impl(LoggingPlugin())
    plugin_registry.load_plugin_with_hooks_impl(ConfigHelpPlugin())
    plugin_registry.load_plugin_with_hooks_impl(CoreConfigDefinitionPlugin())
    plugin_registry.load_plugin_with_hooks_impl(EnvironmentVarsConfigPlugin())
    plugin_registry.load_plugin_with_hooks_impl(RuntimeStateInitializePlugin())
    plugin_registry.load_plugin_with_hooks_impl(NewVersionCheckPlugin())
    plugin_registry.load_plugin_with_hooks_impl(NotificationPlugin())
    plugin_registry.load_plugin_with_hooks_impl(IngesterConfigurationPlugin())
    plugin_registry.load_plugin_with_hooks_impl(PropertiesApiPlugin())
    # TODO: should be in run package only
    plugin_registry.add_hook_specs(JobRunHookSpecs)
    plugin_registry.load_plugin_with_hooks_impl(JobConfigIniPlugin())


@hookimpl(tryfirst=True)
def vdk_command_line(root_command: click.Group) -> None:
    """
    Register commands
    """
    from taurus.vdk.builtin_plugins.run.cli_run import run
    from taurus.vdk.builtin_plugins.version.version import version

    root_command.add_command(run)
    root_command.add_command(version)
