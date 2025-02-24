# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools


__version__ = "0.2.5"

setuptools.setup(
    name="vdk-ipython",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="Ipython extension for VDK",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core", "iPython", "pandas"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={"vdk.plugin.run": ["ipython = vdk.plugin.ipython"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: IPython",
    ],
    extras_require={"data-sources": ["vdk-data-sources"]},
)
