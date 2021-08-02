# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Optional

import click
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.core.context import CoreContext
from taurus.vdk.core.statestore import StoreKey
from taurus.vdk.plugin.plugin import PluginRegistry

log = logging.getLogger(__name__)


@dataclass
class ParsedCall:
    """
    Parsed Hook Call.
    """

    def __init__(self, name: str, kwargs: Dict[str, Any]) -> None:
        self.__dict__.update(kwargs)
        self._name = name

    def __repr__(self) -> str:
        """
        :return: The hook call invocation as string
        """
        d = self.__dict__.copy()
        del d["_name"]
        return f"<ParsedCall {self._name!r}(**{d!r})>"


class HookRecorder:
    """Record all hooks invocations.

    This wraps all the hook calls/invocations, recording each call
    before propagating the normal calls.
    """

    def __init__(self, plugin_registry: PluginRegistry) -> None:
        self._plugin_registry = plugin_registry
        self.calls: List[ParsedCall] = []

        def before(hook_name: str, hook_impls: Any, kwargs: Any) -> None:
            print(
                f"------>> About to call hook {hook_name}\n"
                f"         with args:\n"
                f"         {kwargs}.\n"
                f"         Hook Impl: {hook_impls}",
                file=sys.stderr,
            )
            self.calls.append(ParsedCall(hook_name, kwargs))

        def after(outcome: Any, hook_name: str, hook_impls: Any, kwargs: Any) -> None:
            print(
                f"<<------ Finished call hook {hook_name}\n"
                f"         with args:\n"
                f"         {kwargs}.\n"
                f"         Hook Impl: {hook_impls}\n",
                f"         Outcome: {vars(outcome)}",
                file=sys.stderr,
            )

        self._undo_wrapping = (
            self._plugin_registry.plugin_manager().add_hookcall_monitoring(
                before, after
            )
        )

    def finish_recording(self) -> None:
        """
        Do not record hook calls anymore.
        """
        self._undo_wrapping()

    def get_calls(self) -> List[ParsedCall]:
        """
        Get a list of currently record calls
        """
        return [call for call in self.calls]


@click.command(help="Print hello")
@click.pass_context
def hello(ctx: click.Context) -> None:
    """
    Just prints hello for testing purposes.
    """
    click.echo(f"Hello! Nice to meet you. Here are some nerdy details about me:")
    import json

    def _default_handler(o: Any) -> Any:
        from taurus.vdk.core.context import CoreContext
        from taurus.vdk.core.config import Configuration

        if (
            isinstance(o, click.core.Context)
            or isinstance(o, JobContext)
            or isinstance(o, CoreContext)
            or isinstance(o, Configuration)
        ):
            return vars(o)
        return str(o)

    click.echo(
        f"My context is {json.dumps(vars(ctx), default=_default_handler, indent=4, sort_keys=True)}"
    )


class DebugPlugins:
    """
    Plugin which adds some debug functionalities
    """

    def __init__(self) -> None:
        self.when = 1
        self.hook_recorder: Optional[HookRecorder] = None

    @hookimpl
    def vdk_start(
        self, plugin_registry: PluginRegistry, command_line_args: List
    ) -> None:
        """
        check if debug is needed and active it if yes.
        We also check with env variable.
        We do not use vdk_configure hook in order to trigger the recorder
        at earliest moment possible.
        """
        if "--debug-hooks" in command_line_args:
            # a bit hacky but works for hidden options
            command_line_args.remove("--debug-hooks")
            self.hook_recorder = HookRecorder(plugin_registry)
        if os.getenv("VDK_DEBUG_HOOKS_ENABLED", "no") == "yes":
            self.hook_recorder = HookRecorder(plugin_registry)

    def set_debug_hooks(self, ctx: click.Context, param: Any, value: Any):
        self.hook_recorder = HookRecorder(ctx.obj.plugin_registry)

    @hookimpl
    def vdk_initialize(self, context: CoreContext) -> None:
        plugin_registry = context.plugin_registry
        log.debug(f"Plugins loaded\n: {plugin_registry}")

    @hookimpl
    def vdk_command_line(self, root_command: click.Group) -> None:
        """
        Modify command line arguments to add debug option with callback (instead of above appraoch)
        """
        root_command.add_command(hello)
        self.add_debug_flag(root_command)

    @staticmethod
    def add_debug_flag(root_command):
        def set_debug(ctx: click.Context, param: Any, value: Any) -> None:
            if value and not ctx.resilient_parsing:
                log.debug("Enabling debug")
                core_context = cast(CoreContext, ctx.obj)
                core_context.state.set(StoreKey[bool]("vdk.debug"), True)

        debug_option = click.option(
            "--debug",
            "-D",
            type=click.BOOL,
            is_eager=True,
            expose_value=False,
            default=False,
            is_flag=True,
            callback=set_debug,
            help="Run the command in debug mode",
        )
        run_cmd = cast(click.Command, root_command.get_command(None, "run"))
        if run_cmd:
            root_command.add_command(debug_option(run_cmd))
