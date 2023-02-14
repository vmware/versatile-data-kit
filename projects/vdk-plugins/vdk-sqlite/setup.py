# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import setuptools

"""
Builds a package with the help of setuptools in order for this package to be imported in other projects
"""

__version__ = "0.1.3"

setuptools.setup(
    name="vdk-sqlite",
    version=__version__,
    install_requires=["vdk-core", "tabulate"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    include_package_data=True,
    entry_points={"vdk.plugin.run": ["vdk-sqlite = vdk.plugin.sqlite.sqlite_plugin"]},
)
