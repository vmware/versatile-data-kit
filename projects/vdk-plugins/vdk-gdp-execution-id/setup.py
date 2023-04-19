# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

__version__ = "0.0.1"

setuptools.setup(
    name="vdk-gdp-execution-id",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="This Versatile Data Kit SDK plugin is a Generative Data Pack, that expands each ingested dataset "
    "with the execution ID detected during data job run.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=[
        "vdk-core",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={
        "vdk.plugin.run": [
            "vdk-gdp-execution-id = vdk.plugin.gdp.execution_id.gdp_execution_id_plugin"
        ]
    },
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
