#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

if ! which python3 >/dev/null 2>&1 ; then
  echo "ERROR:"
  echo "Please install python 3.7+. Build cannot continue without it."
  echo "If you are new to python:"
  echo "There are some awesome tools for installing and managing python which we recommend:"
  echo " - conda - https://conda.io/projects/conda/en/latest/user-guide/getting-started.html"
  echo " - pyenv - https://github.com/pyenv/pyenv"
  echo "      - If you use pyenv we also recommend https://github.com/pyenv/pyenv-virtualenv"
  echo ""
  exit 1
fi

cd "$(dirname $0)" || exit 1
cd ..

echo "install dependencies from requirements.txt (used for development and testing)"
pip install --upgrade-strategy eager -U -r requirements.txt

echo "Setup git hook scripts with pre-commit install"
pip install pre-commit
pre-commit install --hook-type commit-msg --hook-type pre-commit

echo "Install the project in editable mode (develop mode)"
pip install --upgrade-strategy eager -U -e .

echo "Run unit tests and generate coverage report"
pip install pytest-cov
pytest --junitxml=tests.xml --cov vdk --cov-report term-missing --cov-report xml:coverage.xml

echo "Done"
