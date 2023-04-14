# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils import output_printer
from vdk.internal.control.utils.output_printer import OutputFormat
from vdk.internal.control.utils.version_utils import __version__
from vdk.internal.control.utils.version_utils import build_details


@click.command(help="Prints the version of the client")
@cli_utils.output_option()
def version(output: str):
    if output == OutputFormat.TEXT.value:
        click.echo(f"""Version: {__version__}\nBuild details: {build_details()}""")
    else:
        data = {"version": __version__, "build_details": build_details()}
        output_printer.create_printer(output).print_dict(data)
