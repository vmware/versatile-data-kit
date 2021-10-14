# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Container
from typing import List
from typing import Optional
from typing import Tuple

import click
from vdk.api.plugin.hook_markers import hookspec
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext


class ConnectionHookSpec:
    """
    These are hook specifications that enable plugins to hook at connection events during cursor execution.
    """

    @hookspec
    def validate_operation(
        self, operation: str, parameters: Optional[Container]
    ) -> None:
        pass

    @hookspec
    def decorate_operation(
        self, decoration_cursor: DecorationCursor, managed_operation: ManagedOperation
    ) -> None:
        pass

    @hookspec
    def recover_operation(self, recovery_cursor: RecoveryCursor) -> None:
        pass
