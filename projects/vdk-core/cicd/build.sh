#!/bin/bash -e

# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

cd "$(dirname $0)" || exit 1
cd ..


echo "install dependencies from requirements.txt (used for development and testing)"
export PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL:-https://test.pypi.org/simple/}
pip install --extra-index-url $PIP_EXTRA_INDEX_URL -r requirements.txt

echo "Setup git hook scripts with pre-commit install"
pre-commit install

echo "Install the project in editable mode (develop mode)"
pip install -e .

echo "Install common vdk test utils library"
pip install -e plugins/vdk-test-utils

echo "Run unit tests and generate coverage report"
pip install pytest-cov
pytest --junitxml=tests.xml --cov taurus --cov-report term-missing --cov-report xml:coverage.xml
