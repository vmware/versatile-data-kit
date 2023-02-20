# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

"""
Builds a package with the help of setuptools in order for this package to be imported in other projects

"plugin-package-template" is the name of the package which contains the plugin/s.

"plugin-template" is the name of the plugin contained within this package. Note that you can include
more than one plugin in a single package. Also note that the contained plugin may have the same name as the package.

"plugin_template" is the Python file which contains the plugin hooks for the corresponding plugin.
"""

__version__ = "0.1.0"

setuptools.setup(
    name="vdk-control-api-auth",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="Versatile Data Kit plugin library provides support for "
    "authentication.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["requests", "requests_oauthlib"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
