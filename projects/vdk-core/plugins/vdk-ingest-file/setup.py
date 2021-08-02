# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import setuptools

__version__ = "0.1.0"

setuptools.setup(
    name="vdk-ingest-file",
    version=__version__,
    install_requires=["vdk-core"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={
        "vdk.plugin.run": ["vdk-ingest-file = taurus.vdk.ingest_file_plugin"]
    },
)
