# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools

setuptools.setup(
    name="vdk-local-differential-privacy",
    version="0.1",
    description="local-differential-privacy plugin for use during ingestion",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={
        "vdk.plugin.run": [
            "vdk-local-differential-privacy-plugin = vdk.plugin.local_differential_privacy.differential_privacy_plugin",
        ]
    },
)
