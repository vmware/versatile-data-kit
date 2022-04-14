# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.plugin.marquez.marquez_server import MarquezInstaller


@click.command(
    name="marquez-server",
    help="Starts or stops a local Marquez Server."
    """
              TODO: Add description
              """,
)
@click.option(
    "--start",
    is_flag=True,
    help="Start a local Marquez Server.",
)
@click.option(
    "--stop",
    is_flag=True,
    help="Removes and stop local marquez server. Will delete all recorded data as well.",
)
@click.option(
    "--status",
    is_flag=True,
    help="Returns whether a local marquez server is currently running.",
)
def server(start, stop, status):
    flags = 0
    if start:
        flags += 1
    if stop:
        flags += 1
    if status:
        flags += 1

    if flags != 1:
        click.echo(
            "Exactly one of --install, --uninstall, or --status options should be specified"
        )
    else:
        installer = MarquezInstaller()
        if start:
            installer.start()
        elif stop:
            installer.stop()
        else:
            installer.check_status()


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(server)
