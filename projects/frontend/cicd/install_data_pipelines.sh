#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

###
# This script generates the dependencies tree, installs the packages needed,
# evaluates the build_data_pipelines_sh script, then
# lints them to verify format, builds the UI application and runs the unit tests.
###

if ! which npm >/dev/null 2>&1 ; then
  echo "ERROR:"
  echo "Please install npm 8.5.5+. Install cannot continue without it."
  exit 1
fi
echo "Logging npm engines version..."
npm version

cd "$(dirname $0)" || exit 1
cd "../data-pipelines/gui"

echo "Removing package lock if available..."
rm -f "package-lock.json"

shared_dist_dir="../../shared-components/gui/dist/shared"
if [ -d "$shared_dist_dir" ]
then
  echo "Linking the shared-components dist rebuild found..."
  npm link "$shared_dist_dir"
else
  echo "No shared-components dist rebuild found."
fi

echo "Install Dependencies..."
npm install

echo "Running linking script..."
sh "../../cicd/build_data_pipelines.sh"

echo "Linting all projects & sub-projects..."
npm run lint

echo "Building the UI Wrapper Project..."
npm run build:ui

echo "Testing all projects & sub-projects... (--watch=false to put exit code 0 after finishing)"
npm run test:headless
