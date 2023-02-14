#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

cd "$(dirname $0)" || exit 1
cd ..

pip install -r requirements.txt

echo "Install the project in editable mode (develop mode)"
pip install -e .

echo "Run unit tests and generate coverage report"
pip install pytest-cov
pytest --junitxml=tests.xml --cov vdk --cov-report term-missing --cov-report xml:coverage.xml
