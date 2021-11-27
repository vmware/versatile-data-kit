# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.internal.control.configuration.defaults_config import (
    reset_default_rest_api_url,
)
from vdk.internal.control.configuration.defaults_config import reset_default_team_name
from vdk.internal.control.configuration.defaults_config import (
    write_default_rest_api_url,
)
from vdk.internal.control.configuration.defaults_config import write_default_team_name


# Default command implies parity for set-default and reset-default sections bellow.
# Each option that supports set-default is expected to implement reset-default.


@click.command(
    name="set-default",
    help="Set defaults that will be used in the commands of the tool.",
)
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    help="Set the default team name that will be used in all the commands that require a team.",
)
@click.option(
    "-u",
    "--rest-api-url",
    type=click.STRING,
    help="Set the default REST API url that will be used in all the commands that require it.",
)
@click.pass_context
def set_default_command(ctx, team: str, rest_api_url: str):
    if team is not None:
        write_default_team_name(team)
    if rest_api_url is not None:
        write_default_rest_api_url(rest_api_url)


@click.command(
    name="reset-default",
    short_help="Reset the defaults that will be used in the commands of the tool.",
    help="Reset the defaults that will be used in the commands of the tool.",
)
@click.option(
    "-t",
    "--team",
    is_flag=True,
    flag_value=True,
    default=False,
    help="Reset the default team name.",
)
@click.option(
    "-u",
    "--rest-api-url",
    is_flag=True,
    flag_value=True,
    default=False,
    help="Reset the default REST API url.",
)
@click.pass_context
def reset_default_command(ctx, team: bool, rest_api_url: bool):
    if team:
        reset_default_team_name()
    if rest_api_url:
        reset_default_rest_api_url()
