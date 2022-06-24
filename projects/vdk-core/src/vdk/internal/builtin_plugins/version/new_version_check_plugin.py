# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import textwrap
from enum import Enum
from typing import List

import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.version import version
from vdk.internal.builtin_plugins.version.new_version_check import Package
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext

log = logging.getLogger(__name__)


class ConfigKey(str, Enum):
    PACKAGE_NAME = "PACKAGE_NAME"
    PACKAGE_INDEX = "PACKAGE_INDEX"
    VERSION_CHECK_PLUGINS = "VERSION_CHECK_PLUGINS"
    VERSION_CHECK_DISABLED = "VERSION_CHECK_DISABLED"


def new_package(package_name: str, package_index: str) -> Package:
    return Package(package_name, package_index)


class NewVersionCheckPlugin:
    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        config_builder.add(
            key=ConfigKey.PACKAGE_NAME.value,
            default_value="vdk-core",
            description="Set distribution package name of the library to check for new version",
        )
        config_builder.add(
            key=ConfigKey.PACKAGE_INDEX.value,
            default_value="https://pypi.org",
            description="Set distribution package name of the library to check for new version",
        )
        config_builder.add(
            key=ConfigKey.VERSION_CHECK_PLUGINS.value,
            default_value=True,
            description="Set to true if plugins should be checked for new version otherwise false",
        )
        config_builder.add(
            key=ConfigKey.VERSION_CHECK_DISABLED.value,
            default_value=False,
            description="Set to true if version check is disabled completely. "
            "It might make sense for managed/cloud executions where version is controlled.",
        )

    @hookimpl
    def vdk_exit(self, context: CoreContext) -> None:
        try:
            package_list = []
            cfg = context.configuration
            is_disabled = cfg.get_value(ConfigKey.VERSION_CHECK_DISABLED.value)
            if is_disabled:
                log.debug(
                    "VERSION_CHECK_DISABLED is set to true, skipping version check."
                )
                return

            package_name = cfg.get_value(ConfigKey.PACKAGE_NAME.value)
            package_index = cfg.get_value(ConfigKey.PACKAGE_INDEX.value)

            if new_package(package_name, package_index).check():
                log.debug(
                    f"New version found for package {package_name} from index {package_index}"
                )
                package_list.append(package_name)

            if cfg.get_value(ConfigKey.VERSION_CHECK_PLUGINS.value):
                log.debug("Will check for newer versions for all installed plugins.")
                for dist_name, _ in version.list_installed_plugins():
                    if new_package(dist_name, package_index).check():
                        package_list.append(dist_name)

            self._print_new_version_message(package_list, package_index)
        except Exception as e:
            log.debug(
                f"Could not check for new version release. "
                f"Error was {e}. We are ignoring the error."
            )

    @staticmethod
    def _print_new_version_message(package_list: List[str], package_index: str) -> None:
        """
        Prints out a new version message for the listed packages.

        :param package_list: list of package names
        :param package_index: package index included in the printed `pip install` command
        """
        if not package_list:
            return
        not_single_package = len(package_list) > 1

        # if package index is not specified that we fetch it from pip repo (pypi.org)
        extra_index_if_needed = (
            f"--extra-index-url {package_index}"
            if (package_index and (package_index != "https://pypi.org"))
            else ""
        )
        pip_command = "pip install --upgrade-strategy eager -U"
        main_message = f"New version{'s' if not_single_package else ''} for {', '.join(package_list)} {'are' if not_single_package else 'is'} available."
        install_message = (
            f"{pip_command} {' '.join(package_list)} {extra_index_if_needed}"
        )
        # We are using eager strategy so that if there's new version of a plugin that satisfies the requirements
        # of the main package we want to upgrade to it.
        click.echo(
            f"""
    ******************************************************************************************

    {textwrap.fill(main_message, 80, subsequent_indent="    ")}

    Please update to latest version by using:
    {install_message}

    ******************************************************************************************
            """,
            err=True,
        )
