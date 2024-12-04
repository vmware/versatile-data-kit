# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools


__version__ = "0.3.0"

setuptools.setup(
    name="vdk-oauth-auth",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="Versatile Data Kit SDK plugin adds Oauth support.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=[
        "vdk-core",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={"vdk.plugin.run": ["vdk-oauth-auth = vdk.plugin.oauth.oauth_plugin"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)