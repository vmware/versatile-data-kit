# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import setuptools

"""
Builds a package with the help of setuptools in order for this package to be imported in other projects
"""
__version__ = "0.1.2"

setuptools.setup(
    name="vdk-plugin-control-cli",
    version=__version__,
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
