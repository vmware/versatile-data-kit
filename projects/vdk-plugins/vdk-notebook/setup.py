# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools


__version__ = "0.1.0"

setuptools.setup(
    name="vdk-notebook",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="A VDK plugin for working with notebooks",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core", "vdk-jupyter", "vdk-ipython"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={"vdk.plugin.run": ["notebook = vdk.plugin.notebook.notebook_plugin"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires="~=3.7",
)
