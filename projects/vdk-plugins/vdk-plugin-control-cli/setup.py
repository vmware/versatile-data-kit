# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
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
    url="https://github.com/vmware/versatile-data-kit",
    description="Versatile Data Kit SDK plugin exposing CLI commands for managing the lifecycle of a Data Jobs.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core", "vdk-control-cli", "requests"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={
        "vdk.plugin.run": [
            "vdk-plugin-control-cli = vdk.plugin.control_cli_plugin.vdk_plugin_control_cli",
            "vdk-control-service-properties = vdk.plugin.control_cli_plugin.properties_plugin",
            "vdk-execution-skip = vdk.plugin.control_cli_plugin.execution_skip",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
