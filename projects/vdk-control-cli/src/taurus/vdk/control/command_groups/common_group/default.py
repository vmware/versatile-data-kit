# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from taurus.vdk.control.configuration.defaults_config import reset_default_team_name
from taurus.vdk.control.configuration.defaults_config import write_default_team_name

# Default command implies parity for set-default and reset-default sections bellow.
# Each option that supports set-default is expected to implement reset-default.


@click.command(
    name="set-default",
    help="Set the defaults that will be used in the commands of the tool.",
)
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    help="Set the default team name that will be used in all the commands that require a team.",
)
@click.pass_context
def set_default_command(ctx, team: str):
    if team is not None:
        write_default_team_name(team)


@click.command(
    name="reset-default",
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
@click.pass_context
def reset_default_command(ctx, team: bool):
    if team:
        reset_default_team_name()
