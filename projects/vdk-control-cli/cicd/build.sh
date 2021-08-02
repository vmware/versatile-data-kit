#!/bin/bash -e

# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

cd "$(dirname $0)" || exit 1
cd ..


echo "install dependencies from requirements.txt (used for development and testing)"
pip install -r requirements.txt

echo "Setup git hook scripts with pre-commit install"
pip install pre-commit
pre-commit install

echo "Install the project in editable mode (develop mode)"
pip install -e .

echo "Run unit tests and generate coverage report"
pip install pytest-cov
pytest --junitxml=tests.xml --cov taurus --cov-report term-missing --cov-report xml:coverage.xml
