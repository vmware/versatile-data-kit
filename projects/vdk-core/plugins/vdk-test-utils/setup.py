# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import setuptools


__version__ = "0.1.2"


setuptools.setup(
    name="vdk-test-utils",
    version=__version__,
    install_requires=["vdk-core"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
)
