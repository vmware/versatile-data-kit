#!/bin/bash -e
# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# This script needs the following environment variables:
# ARTIFACTORY_USER, ARTIFACTORY_PASS - Artifactory credentials

cd build/python
python3.7 -m venv venv
source venv/bin/activate

pip install -U pip setuptools wheel twine
pip install -r requirements.txt

rm -rf dist/
python setup.py sdist --formats=gztar
twine upload --repository-url "$PIP_REPO_UPLOAD_URL" -u "$PIP_REPO_UPLOAD_USER_NAME" -p "$PIP_REPO_UPLOAD_USER_PASSWORD" dist/*tar.gz
