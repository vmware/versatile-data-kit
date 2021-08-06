# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

__version__ = "0.1.3"

setuptools.setup(
    name="vdk-trino",
    version=__version__,
    description="Versatile Data Kit SDK plugin provides support for trino database and trino transformation templates.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core", "trino"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    include_package_data=True,
    entry_points={"vdk.plugin.run": ["vdk-trino = taurus.vdk.trino_plugin"]},
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
    ],
)
