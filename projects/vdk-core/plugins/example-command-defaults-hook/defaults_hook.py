# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_utils import set_defaults_for_all_commands
from vdk.api.plugin.plugin_utils import set_defaults_for_specific_command


@hookimpl
def vdk_command_line(root_command: click.Group):
    set_defaults_for_specific_command(
        root_command, "example-extra-command", {"color": "blue", "area": "green"}
    )
