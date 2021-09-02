# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import setuptools

"""
Builds a package with the help of setuptools in order for this package to be imported in other projects
"""
__version__ = "0.1.2"

setuptools.setup(
    name="taurus-vdk",
    version=__version__,
    install_requires=["vdk-core", "vdk-plugin-control-cli", "vdk-trino"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
    ],
)
