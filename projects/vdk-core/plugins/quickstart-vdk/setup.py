# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

__version__ = "0.1.dev1"

setuptools.setup(
    name="quickstart-vdk",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="Versatile Data Kit SDK packaging containing common plugins to get started quickly using it.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=[
        "vdk-core",
        "vdk-plugin-control-cli",
        "vdk-trino",
        "vdk-sqlite",
        "vdk-ingest-http",
        "vdk-ingest-file",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
