# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

"""
Builds a package with the help of setuptools in order for this package to be imported in other projects
"""

__version__ = "0.3.0"

setuptools.setup(
    name="vdk-lineage",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="VDK Lineage plugin collects lineage (input -> job -> output) information "
    "and send it to a pre-configured destination.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=[
        "vdk-core",
        "vdk-lineage-model",
        "sqlparse",
        "sqllineage",
        "openlineage-integration-common",
        "openlineage-python",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    include_package_data=True,
    entry_points={
        "vdk.plugin.run": [
            "vdk-lineage = vdk.plugin.lineage.plugin_lineage",
            "vdk-marquez = vdk.plugin.marquez.marquez_plugin",
        ]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
