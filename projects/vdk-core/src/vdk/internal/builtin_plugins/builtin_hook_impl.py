# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import time
import uuid
from datetime import datetime
from typing import List

import click
from vdk.api.plugin.connection_hook_spec import (
    ConnectionHookSpec,
)
from vdk.api.plugin.core_hook_spec import JobRunHookSpecs
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal import vdk_build_info
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.builtin_plugins.config.config_help import ConfigHelpPlugin
from vdk.internal.builtin_plugins.config.log_config import LoggingPlugin
from vdk.internal.builtin_plugins.config.vdk_config import CoreConfigDefinitionPlugin
from vdk.internal.builtin_plugins.config.vdk_config import EnvironmentVarsConfigPlugin
from vdk.internal.builtin_plugins.config.vdk_config import JobConfigIniPlugin
from vdk.internal.builtin_plugins.connection.connection_plugin import (
    QueryDecoratorPlugin,
)
from vdk.internal.builtin_plugins.debug.debug import DebugPlugins
from vdk.internal.builtin_plugins.ingestion.ingester_configuration_plugin import (
    IngesterConfigurationPlugin,
)
from vdk.internal.builtin_plugins.job_properties.properties_api_plugin import (
    PropertiesApiPlugin,
)
from vdk.internal.builtin_plugins.notification.notification import NotificationPlugin
from vdk.internal.builtin_plugins.termination_message.writer import (
    TerminationMessageWriterPlugin,
)
from vdk.internal.builtin_plugins.version.new_version_check_plugin import (
    NewVersionCheckPlugin,
)
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.internal.plugin.plugin import PluginRegistry

log = logging.getLogger(__name__)


class RuntimeStateInitializePlugin:
    """
    Initialize in the StateStore common runtime attributes
    """

    @hookimpl(tryfirst=True)
    def vdk_initialize(self, context: CoreContext) -> None:
        """
        Setup common state attributes of the app (CommonStoreKeys).

        Configuration can override an attempt/op/execution id.

        Attempt id and Execution id are extracted from env variables.
        If not present they are auto generated.

        If auto generated:
        * Attempt id format is uuid + timestamp + five random chars.
        * Execution id is attempt id minus last 6 chars.
        * Op id is equal to execution id.
        """
        op_id = context.configuration.get_value(vdk_config.OP_ID)
        execution_id = context.configuration.get_value(vdk_config.EXECUTION_ID)
        attempt_id = context.configuration.get_value(vdk_config.ATTEMPT_ID)

        if not attempt_id:
            # Generate attempt id if execution id not present.
            if not execution_id:
                # UUID is 36 chars
                attempt_id = f"{str(uuid.uuid4())}-{str(int(time.time()))}-{str(uuid.uuid4())[:5]}"
            # Use execution id to generate attempt id.
            else:
                attempt_id = f"{execution_id}-{str(uuid.uuid4())[:5]}"
            # If env is cloud we must print a warning.
            if context.configuration.get_value(vdk_config.LOG_CONFIG) == "CLOUD":
                log.warning(
                    f"Attempt ID not found in env or configuration. Using auto generated attempt_id: {attempt_id}"
                )

        if not execution_id:
            # Delete everything after the last '-' character in the attempt id (inclusive)
            execution_id = "-".join(attempt_id.split("-")[:-1])

        if not op_id:
            op_id = execution_id

        log.info(
            f"Setting: OP_ID: {op_id}, ATTEMPT_ID: {attempt_id}, EXECUTION_ID: {execution_id}"
        )
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
    plugin_registry.load_plugin_with_hooks_impl(TerminationMessageWriterPlugin())
    # connection plugins
    plugin_registry.add_hook_specs(ConnectionHookSpec)
    plugin_registry.load_plugin_with_hooks_impl(QueryDecoratorPlugin())


@hookimpl(tryfirst=True)
def vdk_command_line(root_command: click.Group) -> None:
    """
    Register commands
    """
    from vdk.internal.builtin_plugins.run.cli_run import run
    from vdk.internal.builtin_plugins.version.version import version

    root_command.add_command(run)
    root_command.add_command(version)
