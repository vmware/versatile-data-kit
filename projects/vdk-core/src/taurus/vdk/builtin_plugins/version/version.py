# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os

import click
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution
from taurus.api.plugin.hook_markers import GROUP_NAME
from taurus.vdk import vdk_build_info

try:  # importlib.metadata is used in 3.8+, importlib_metadata is used in 3.7
    from importlib import metadata
except ImportError as e:
    import importlib_metadata as metadata

log = logging.getLogger(__name__)

# Returns the version of the package named dist_name
def _version(
    dist_name="vdk-core",
):  # Change default value if project is renamed and does not equal the setuptools metadata.name
    try:
        return get_distribution(dist_name).version
    except DistributionNotFound:  # pragma: no cover
        return "unknown"


def _dist_name(dist: metadata.PathDistribution):
    return dist.metadata["Name"]


def build_details():
    try:
        build = [
            f"{key}={value}"
            for key, value in vdk_build_info.__dict__.items()
            if not key.startswith("_")
        ]
        return ", ".join(build)
    except Exception as e:
        log.warning(f"Failed to get build details due to error: {e}")


def list_installed_plugins():
    """
    :return: List of pairs (plugin distribution name, plugin name)
    """
    dist_plugin_pairs = []
    for dist in list(metadata.distributions()):
        for ep in dist.entry_points:
            if ep.group == GROUP_NAME:
                dist_plugin_pairs.append((_dist_name(dist), ep.name))
    return dist_plugin_pairs


def list_installed_plugins_versions():
    """
    :return: a string "*plugin_name*, version *plugin_version \n *next_plugin_name*, version *next_plugin_version*" etc
    """
    dist_plugin_pairs = list_installed_plugins()

    plugin_list = [
        plugin + " (from package " + dist + ", version " + _version(dist) + ")"
        for dist, plugin in dist_plugin_pairs
    ]
    return "\n".join(plugin_list) if len(plugin_list) > 0 else "None"


def get_version_info():
    return (
        f"Version: {_version()}{os.linesep}"
        f"Build details: {build_details()}{os.linesep}{os.linesep}"
        f"Installed plugins:{os.linesep}{list_installed_plugins_versions()}"
    )


@click.command(help="Prints the version of the client and exits")
@click.pass_context
def version(ctx: click.Context):
    # all necessary info is printed by LogVersionInfoPlugin
    click.echo(
        f"Data Jobs Development Kit (VDK){os.linesep}{get_version_info()}", err=True
    )
    click.echo("-" * 80, err=True)
    pass
