# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools


__version__ = "0.1.2"


setuptools.setup(
    name="vdk-test-utils",
    version=__version__,
    description="Provides utilities for testing Versatile Data Kit SDK plugins.",
    long_description=pathlib.Path("README.md").read_text(),
    install_requires=["vdk-core"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
)
