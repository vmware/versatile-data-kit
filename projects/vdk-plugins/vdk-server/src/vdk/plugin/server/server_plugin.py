# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK Server plugin script.
"""
import logging
from typing import Optional

import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.plugin.server.installer import Installer

log = logging.getLogger(__name__)


@click.command(
    name="server",
    help="Installs (and runs) or uninstalls a local Control Service."
    """
        This command facilitates the management of the local VDK Control Service Server.
        It's designed to simplify the setup process for development and testing environments.
        For production deployment of VDK Control Service see
        https://github.com/vmware/versatile-data-kit/wiki/Versatile-Data-Kit-Control-Service

        Examples:

        \b
        # Install the VDK Control Service Server. It can then be acess at http://localhost:8092.
        # It will set default API url to http://localhost:8092 as well for vdk CLI.
        vdk server --install

        \b
        # Check status (is it installed and running)
        vdk server --status

        \b Uninstall and remove the VDK Control Service Server.
        vdk server --uninstall

         """,
)
@click.option(
    "-i",
    "--install",
    is_flag=True,
    help="Installs a local Control Service.",
)
@click.option(
    "-u",
    "--uninstall",
    is_flag=True,
    help="Removes a previous Control Service installation.",
)
@click.option(
    "-s",
    "--status",
    is_flag=True,
    help="Returns whether a local Control Service is currently installed.",
)
@click.option(
    "-f",
    "--file",
    help="Pass custom values.yaml file with helm chart configuration for Control Service installation..",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True, resolve_path=True),
    required=False,
    help="The path to a values.yaml file with control service helm configuration."
    " Used this to fine tune the deployment of hte control service when running vdk server --install."
    " See all configuration options documented in https://bit.ly/vdk-helm-values",
)
def server(install, uninstall, status, file: Optional[str]):
    flags = 0
    if install:
        flags += 1
    if uninstall:
        flags += 1
    if status:
        flags += 1

    if flags != 1:
        click.echo(
            "Exactly one of --install, --uninstall, or --status options should be specified"
        )
    else:
        installer = Installer(file)
        if install:
            installer.install()
        elif uninstall:
            installer.uninstall()
        else:
            installer.check_status()


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(server)
