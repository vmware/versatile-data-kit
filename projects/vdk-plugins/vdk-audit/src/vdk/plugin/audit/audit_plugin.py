# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 VMware, Inc.
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


class AuditPlugin:
    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder)

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        self._config = AuditConfiguration(context.core_context.configuration)

        logging.getLogger(__name__).error("Start:")
        logging.getLogger(__name__).error(not self._config.enabled())
        if not self._config.enabled():
            return

        not_permitted_events_list = self._config.forbidden_events_list().split(";")

        def _audit(event, args):
            if any(
                event in not_permitted_event
                for not_permitted_event in not_permitted_events_list
            ):
                logging.getLogger(__name__).warning(
                    f'[Audit] Detected NOT permitted operation "{event}" with '
                    f'arguments "{args}" '
                )

                if self._config.exit_on_not_permitted_event():
                    logging.getLogger(__name__).error(
                        f"[Audit] Terminating the data job due to the NOT "
                        f'permitted operation "{event}" with arguments "{args}" '
                    )
                    os._exit(0)

        sys.addaudithook(_audit)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(AuditPlugin(), "audit-plugin")
