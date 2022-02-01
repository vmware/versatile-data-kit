#!/bin/bash -e

# Copyright 2021 VMware, Inc.
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

export PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL:-https://test.pypi.org/simple/}

echo "Update pip to newest version"
pip install -U pip

# Below line uses --use-deprecated=legacy-resolver to temporary workaround a
# dependency backtracking issue.
# TODO: Remove the use of the legacy resolver once latest pip works as expected.
echo "install dependencies from requirements.txt (used for development and testing)"
pip install --use-deprecated="legacy-resolver" --extra-index-url $PIP_EXTRA_INDEX_URL -r requirements.txt

echo "Setup git hook scripts with pre-commit install"
pre-commit install

# Below line uses --use-deprecated=legacy-resolver to temporary workaround a
# dependency backtracking issue.
# TODO: Remove the use of the legacy resolver once latest pip works as expected.
echo "Install the vdk-core in editable mode (develop mode)"
pip install --use-deprecated="legacy-resolver" -e .

# Below line uses --use-deprecated=legacy-resolver to temporary workaround a
# dependency backtracking issue.
# TODO: Remove the use of the legacy resolver once latest pip works as expected.
echo "Install common vdk test utils library (in editable mode)"
pip install --use-deprecated="legacy-resolver" -e ../vdk-plugins/vdk-test-utils

# Below line uses --use-deprecated=legacy-resolver to temporary workaround a
# dependency backtracking issue.
# TODO: Remove the use of the legacy resolver once latest pip works as expected.
echo "Run unit tests and generate coverage report"
pip install --use-deprecated="legacy-resolver" pytest-cov
pytest --junitxml=tests.xml --cov vdk --cov-report term-missing --cov-report xml:coverage.xml

echo "Done"
