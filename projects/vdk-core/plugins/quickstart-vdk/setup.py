# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

__version__ = "0.1.2"

setuptools.setup(
    name="quickstart-vdk",
    description="Versatile Data Kit SDK packaging containing common plugins to get started quickly using it.",
    long_description=pathlib.Path("README.md").read_text(),
    version=__version__,
    install_requires=[
        "vdk-core",
        "vdk-plugin-control-cli",
        "vdk-trino",
        "vdk-ingest-http",
        "vdk-ingest-file",
    ],
)
