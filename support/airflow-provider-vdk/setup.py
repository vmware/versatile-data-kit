# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from setuptools import find_packages
from setuptools import setup

with open("README.md") as fh:
    long_description = fh.read()

"""Perform the package airflow-provider-vdk setup."""
setup(
    name="airflow-provider-vdk",
    version="0.0.1",
    description="Airflow provider for Versatile Data Kit.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "apache_airflow_provider": ["provider_info=vdk.__init__:get_provider_info"]
    },
    license="Apache License 2.0",
    packages=["vdk", "vdk.hooks", "vdk.sensors", "vdk.operators"],
    install_requires=[
        "apache-airflow>=2.0",
        "tenacity>=6.2.0",
        "vdk-core",
        "vdk-control-cli",
    ],
    setup_requires=["setuptools", "wheel"],
    author="Versatile Data Kit Development Team",
    author_email="versatile-data-kit@vmware.com",
    url="https://github.com/vmware/versatile-data-kit",
    python_requires="~=3.7",
)
