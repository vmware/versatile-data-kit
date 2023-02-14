# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools


__version__ = "0.2.dev1"

setuptools.setup(
    name="quickstart-vdk",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="Versatile Data Kit SDK packaging containing common plugins to get started quickly using it.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    # If you add a new dependency to quickstart-vdk, add its location to quickstart-vdk/.plugin-ci.yml in
    # quickstart_vdk_locations, so that quickstart-vdk would be tested when the new dependency is upgraded
    install_requires=[
        "vdk-core",
        "vdk-plugin-control-cli",
        "vdk-sqlite",
        "vdk-ingest-http",
        "vdk-ingest-file",
        "vdk-server",
        "vdk-logging-format",
    ],
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
