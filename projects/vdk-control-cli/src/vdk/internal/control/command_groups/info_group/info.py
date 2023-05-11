# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import click
import click_spinner
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils.output_printer import OutputFormat

log = logging.getLogger(__name__)


@click.command(
    help="Get Control Service Information. "
    "Get the current version of the Control Service and the supported python versions."
)
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    default=load_default_team_name(),
    required=True,
    prompt="Job Team",
    help="The team name to which the job belong to.",
)
@cli_utils.rest_api_url_option()
@cli_utils.check_required_parameters
@cli_utils.output_option()
def info(team: str, rest_api_url: str, output: str):
    click.echo("Getting control service information...")
    with click_spinner.spinner(disable=(output == OutputFormat.JSON.value)):
        try:
            service_api = ApiClientFactory(rest_api_url).get_service_api()
            result = service_api.info(team_name=team)
        except Exception as e:
            raise VDKException(
                what="Cannot obtain VDK Control Service information.",
                why="Unable to connect to service.",
                consequence="Cannot display service information.",
                countermeasure="Resolve VDK Control Service connectivity issue.",
            ) from e

    click.echo(f"VDK Control service version: {result.api_version}")
    click.echo("Supported python versions:")
    for supported_python_version in result.supported_python_versions:
        click.echo(f"\t{supported_python_version}")
