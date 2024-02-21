# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from typing import List

import click
import requests
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils import output_printer


def find_packages_starting_with(prefix: str) -> List[str]:
    url = "https://pypi.org/simple/"
    headers = {"Accept": "application/vnd.pypi.simple.v1+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = response.json()["projects"]
        filtered_packages = [pkg["name"] for pkg in projects if prefix in pkg["name"]]
        return filtered_packages
    else:
        return []


def list_all_likely_taps() -> List[dict]:
    likely_taps = find_packages_starting_with("tap-")  # get_likely_singer_packages()
    likely_taps.sort()
    taps = []
    for tap_package in likely_taps:
        taps.append(
            dict(name=tap_package, url=f"https://pypi.org/project/{tap_package}")
        )
    return taps


@click.command(
    name="singer",
    help="Explore singer sources (taps) and targets."
    """This command allows you to discover available likely Singer taps (data sources)
and provides relevant information including their PyPI URLs.
Use the --list-taps flag to list all likely tap packages.

Example:
#To list all taps, run:
`vdk singer --list-taps`""",
)
@click.option(
    "--list-taps",
    is_flag=True,
    help="List possible taps that can be used. "
    "It simply searches Python index for possible taps. "
    "Their quality and maturity should be verified separately.",
)
@click.pass_context
@cli_utils.output_option()
def singer(ctx: click.Context, list_taps: bool, output: str):
    if list_taps:
        taps = list_all_likely_taps()
        output_printer.create_printer(output).print_table(taps)
