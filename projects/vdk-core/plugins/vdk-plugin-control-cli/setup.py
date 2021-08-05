# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

"""
Builds a package with the help of setuptools in order for this package to be imported in other projects
"""
__version__ = "0.1.dev2"

setuptools.setup(
    name="vdk-plugin-control-cli",
    version=__version__,
    description="Versatile Data Kit SDK plugin exposing CLI commands for managing the lifecycle of a Data Jobs.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core", "vdk-control-cli", "requests"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={
        "vdk.plugin.run": [
            "vdk-plugin-control-cli = taurus.vdk.vdk_plugin_control_cli",
            "vdk-control-service-properties = taurus.vdk.properties_plugin",
        ]
    },
)
