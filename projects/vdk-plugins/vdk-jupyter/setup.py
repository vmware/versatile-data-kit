# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools


__version__ = "0.0.1"

setuptools.setup(
    name="vdk-jupyter",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="Plugin for helping us read notebook files.",
    install_requires=["vdk-core"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    include_package_data=True,
    entry_points={"vdk.plugin.run": ["vdk-jupyter = vdk.run.nb_data_job"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires="~=3.7",
    setup_requires=["setuptools"],
)