# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

"""
Builds a package with the help of setuptools in order for this package to be imported in other projects
"""

__version__ = "0.1.0"

setuptools.setup(
    name="vdk-singer",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="The plugin provides seamless configuration and execution of Singer Taps and Targets.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=[
        "vdk-core",
        "simplejson",
        "pytz",
        "vdk-control-cli",
        "vdk-data-sources",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    # This is the only vdk plugin specifc part
    # Define entry point called "vdk.plugin.run" with name of plugin and module to act as entry point.
    entry_points={"vdk.plugin.run": ["vdk-singer = vdk.plugin.singer.plugin_entry"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    project_urls={
        "Documentation": "https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-singer",
        "Source Code": "https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-singer",
        "Bug Tracker": "https://github.com/vmware/versatile-data-kit/issues/new/choose",
    },
)
