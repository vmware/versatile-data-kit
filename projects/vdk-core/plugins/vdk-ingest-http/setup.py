# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

__version__ = "0.1.0"

setuptools.setup(
    name="vdk-ingest-http",
    version=__version__,
    description="Versatile Data Kit SDK ingestion plugin to ingest data via http requests.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={
        "vdk.plugin.run": ["vdk-ingest-http = taurus.vdk.ingest_http_plugin"]
    },
)
