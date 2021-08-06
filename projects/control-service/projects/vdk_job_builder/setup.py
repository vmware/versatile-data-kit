# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import setuptools

"""Builds a package with the help of setuptools in order for this package to be imported in other projects
"""

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vdk-job-builder",
    version="0.0.1",
    # author="Example Author",
    author_email="versatiledatakit@groups.vmware.com",
    description="Package which builds Data Jobs with Docker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: Apache Software License",
        # "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
