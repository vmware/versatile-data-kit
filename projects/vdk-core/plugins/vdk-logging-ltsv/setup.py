# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

__version__ = "0.1.0"

setuptools.setup(
    name="vdk-logging-ltsv",
    version=__version__,
    description="Versatile Data Kit SDK plugin that changes logging output to LTSV format.",
    long_description=pathlib.Path("README.md").read_text(),
    install_requires=["vdk-core"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={"vdk.plugin.run": ["vdk-logging-ltsv = taurus.vdk.logging_ltsv"]},
)
