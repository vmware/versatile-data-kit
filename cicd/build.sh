#!/bin/bash -e
# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

echo "Starting build on $(uname -a)."
echo "Will setup local repository"
echo "In order to build all projects following prerequisites will be required:"
echo " - python 3"
echo " - Java 11+ (for control service)"
echo " - Docker (for control service)"
echo "For now we need only Python."
echo ""

if ! which python3 >/dev/null 2>&1 ; then
  echo "ERROR:"
  echo "Please install python 3. Initial setup cannot continue without it."
  echo "If you are new to python:"
  echo "There are some awesome tools for installing and managing python which we recommend:"
  echo " - conda - https://conda.io/projects/conda/en/latest/user-guide/getting-started.html"
  echo " - pyenv - https://github.com/pyenv/pyenv"
  echo "      - If you use pyenv we also recommend https://github.com/pyenv/pyenv-virtualenv"
  echo ""
  exit 1
fi


echo "Setup git hook scripts with pre-commit install"
pip install -q pre-commit
pre-commit install --hook-type commit-msg --hook-type pre-commit

echo ""
echo "You are all setup."
echo ""

projects=($(ls "$SCRIPT_DIR/../projects")) || exit
num_projects="${#projects[@]}"

echo "This is mono repo with $num_projects separate projects for each component of Versatile Data Kit."
echo "Each of them has its own separate and independent build and CICD."
echo ""

echo "Pick which project you want to build, cd there and run ./cicd/build.sh of the project"
echo ""

for project in "${projects[@]}"
do
   echo "> Go to projects/$project"
done

echo ""
