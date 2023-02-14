# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock

from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.core.config import Configuration
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import StateStore


def test_core_context_child_context():
    context = CoreContext(
        MagicMock(spec=IPluginRegistry), MagicMock(spec=Configuration), StateStore()
    )
    child = context.create_child_context()
    grand_child = child.create_child_context()

    assert child != context
    assert grand_child != child
    assert child.state != context.state
    child.state["foo"] = 1
    assert "foo" not in context.state
