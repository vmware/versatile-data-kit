# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from enum import Enum

import click
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.version import version
from taurus.vdk.builtin_plugins.version.new_version_check import Package
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.core.context import CoreContext

log = logging.getLogger(__name__)


class ConfigKey(str, Enum):
    PACKAGE_NAME = "PACKAGE_NAME"
    PACKAGE_INDEX = "PACKAGE_INDEX"
    VERSION_CHECK_PLUGINS = "VERSION_CHECK_PLUGINS"


def new_package(package_index, package_name):
    return Package(package_name, package_index)


class NewVersionCheckPlugin:
    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        config_builder.add(
            key=ConfigKey.PACKAGE_NAME,
            default_value="vdk-core",
            description="Set distribution package name of the library to check for new version",
        )
        config_builder.add(
            key=ConfigKey.PACKAGE_INDEX,
            default_value="https://pypi.org",
            description="Set distribution package name of the library to check for new version",
        )
        config_builder.add(
            key=ConfigKey.VERSION_CHECK_PLUGINS,
            default_value=True,
            description="Set to true if plugins should be checked for new version otherwise false",
        )

    @hookimpl
    def vdk_initialize(self, context: CoreContext) -> None:
        try:
            cfg = context.configuration
            package_name = cfg.get_value(ConfigKey.PACKAGE_NAME)
            package_index = cfg.get_value(ConfigKey.PACKAGE_INDEX)
            self.check_version(package_name, package_index)

            if cfg.get_value(ConfigKey.VERSION_CHECK_PLUGINS):
                log.debug("Will check for newer versions all installed plugins.")
                for dist_name, _ in version.list_installed_plugins():
                    self.check_version(dist_name, package_index, is_plugin=True)
        except Exception as e:
            log.info(
                f"Could not check for new version release. "
                f"Error was {e}. We are ignoring the error."
            )

    @staticmethod
    def check_version(package_name, package_index, is_plugin=False):
        if new_package(package_index, package_name).check():
            # if package index is not specified that we fetch it from pip repo (pypi.org)
            extra_index_if_needed = (
                f"--extra-index-url {package_index}" if package_index else ""
            )
            message = (
                f"New version for a plugin {package_name} is Available"
                if is_plugin
                else f"New Version of {package_name} is Available"
            )
            # We are using eager strategy so that if there's new version of a plugin that satisfies the requirements
            # of the main package we want to upgrade to it.
            pip_command = "pip install --upgrade-strategy eager -U"
            click.echo(
                f"""
                **********************************************************************************************************************

                                                {message}

                  Please update to latest version by using:
                  {pip_command} {package_name} {extra_index_if_needed}

                **********************************************************************************************************************
                """,
                err=True,
            )
