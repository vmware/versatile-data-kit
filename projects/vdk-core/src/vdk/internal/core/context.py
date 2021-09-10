# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass
from typing import List

from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.core.config import Configuration
from vdk.internal.core.statestore import ImmutableStoreKey
from vdk.internal.core.statestore import StateStore
from vdk.internal.core.statestore import StoreKey


# TODO: consider moving some of those (or extracting interface) to vdk.api as they are used by users (plugin
#  developers)


@dataclass(frozen=True)
class CoreContext:
    """
    The context is a special object that hold info about the context in which the current execution is.

    It keeps info about the plugins being loaded and enable manipulating plugins
    It keeps info about how is the current execution being configured.
    It also holds state relevant for the CLI execution.
    """

    plugin_registry: IPluginRegistry
    configuration: Configuration
    # Keep state here, It's mutable and can be edited by plugins as well.
    # Key starting with "vdk." should be reserved for core state and not used by plugins
    # For data job context (run command)
    # there's separate JobContext class that's should be used (see builtin_plugins/run/job_context)
    state: StateStore

    def create_child_context(self):
        """
        You can create a child context if you want to create internal child execution of a CLI execution.
        For example CLI (root level) execution will keep track of generic CLI state.
        Data Job execution being spawned in CLI execution would be a child of that CLI execution and keep track of
        Job execution related state.
        Child context inherits (copies) parent context at the time of creation. Permanent link to parent is not tracked.
        It's kept as key only for reference purposes.
        """

        child_context = CoreContext(
            self.plugin_registry, self.configuration, self.state.clone()
        )
        child_context.state.set(StoreKey[StateStore]("vdk.state.parent"), self.state)
        children_key = ImmutableStoreKey[List[StateStore]]("vdk.state.children")
        if self.state.get(children_key) is None:
            self.state.set(children_key, [])
        self.state.get(children_key).append(child_context.state)
        return child_context
