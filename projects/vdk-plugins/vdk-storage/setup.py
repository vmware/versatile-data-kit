# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

"""
Builds a package with the help of setuptools in order for this package to be imported in other projects
"""

__version__ = "0.1.1"

setuptools.setup(
    name="vdk-storage",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="Library for access to different managed storages",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core", "sqlalchemy"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={"vdk.plugin.run": ["vdk-storage = vdk.plugin.storage.plugin_entry"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    project_urls={
        "Documentation": "https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-storage",
        "Source Code": "https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-storage",
        "Bug Tracker": "https://github.com/vmware/versatile-data-kit/issues/new/choose",
    },
)
