# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import setuptools

"""Builds a package with the help of setuptools in order for this package to be imported in other projects
"""


setuptools.setup(
    name="vdk-defaults-hook",
    version="0.1.0",
    install_requires=["vdk-core"],
    py_modules=["defaults_hook"],
    entry_points={"vdk.plugin.run": ["vdk-defaults-hook = defaults_hook"]},
)
