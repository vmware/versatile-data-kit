# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.internal.control.utils.version_utils import __version__
from vdk.internal.control.utils.version_utils import build_details


@click.command(help="Prints the version of the client")
def version():
    click.echo(f"""Version: {__version__}\nBuild details: {build_details()}""")
