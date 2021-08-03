# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

__version__ = "0.1.0"

setuptools.setup(
    name="vdk-ingest-file",
    version=__version__,
    description="Versatile Data Kit SDK ingestion plugin to ingest data into a file.",
    long_description=pathlib.Path("README.md").read_text(),
    install_requires=["vdk-core"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={
        "vdk.plugin.run": ["vdk-ingest-file = taurus.vdk.ingest_file_plugin"]
    },
)
