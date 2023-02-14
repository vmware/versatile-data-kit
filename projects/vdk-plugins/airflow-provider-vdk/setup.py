# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from setuptools import setup

__version__ = "0.0.1"

with open("README.md") as fh:
    long_description = fh.read()

setup(
    name="airflow-provider-vdk",
    version=__version__,
    description="Airflow provider for Versatile Data Kit.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "apache_airflow_provider": [
            "provider_info=vdk_provider.__init__:get_provider_info"
        ]
    },
    license="Apache License 2.0",
    packages=[
        "vdk_provider",
        "vdk_provider.hooks",
        "vdk_provider.sensors",
        "vdk_provider.operators",
    ],
    install_requires=[
        "apache-airflow>=2.0",
        "tenacity>=6.2.0",
        "vdk-control-api-auth",
        "vdk-control-service-api",
    ],
    setup_requires=["setuptools", "wheel"],
    author="Versatile Data Kit Development Team",
    author_email="versatile-data-kit@vmware.com",
    url="https://github.com/vmware/versatile-data-kit",
    python_requires=">=3.7",
)
