# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools


__version__ = "0.1.0"

setuptools.setup(
    name="vdk-audit-hook",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="Versatile Data Kit SDK Audit Hook plugin restricts not permitted actions.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={
        "vdk.plugin.run": ["vdk-audit-hook = vdk.plugin.audit_hook.audit_hook_plugin"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
