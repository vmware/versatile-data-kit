# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import sys
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.audit.audit_config import add_definitions
from vdk.plugin.audit.audit_config import AuditConfiguration


log = logging.getLogger(__name__)


class AuditPlugin:
    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder)

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        self._config = AuditConfiguration(context.core_context.configuration)

        if not self._config.enabled():
            return

        forbidden_events_list = self._config.forbidden_events_list().split(";")

        def _audit(event, args):
            if any(
                event == not_permitted_event
                for not_permitted_event in forbidden_events_list
            ):
                log.warning(
                    f'[Audit] Detected FORBIDDEN operation "{event}" with '
                    f'arguments "{args}" '
                )

                if self._config.exit_on_forbidden_event():
                    log.error(
                        f"[Audit] Terminating the data job due to the FORBIDDEN "
                        f'operation "{event}" with arguments "{args}" '
                    )
                    os._exit(self._config.exit_code())

        sys.addaudithook(_audit)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(AuditPlugin(), "audit-plugin")
