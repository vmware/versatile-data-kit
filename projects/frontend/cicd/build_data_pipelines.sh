#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

###
# For installing the build prerequisites, consider `install_data_pipelines.sh` script.
# This script is meant to be used, to quickly
# rebuild and link the the @versatiledatakit/data-pipelines in an already bootstrapped development setup.
###

if ! which npm >/dev/null 2>&1 ; then
  echo "ERROR:"
  echo "Please install npm 8.5.5+. Build cannot continue without it."
  exit 1
fi
echo "Logging npm engines version..."
npm version

cd "$(dirname $0)" || exit 1
cd "../data-pipelines/gui"

echo "Build the Data Pipelines Library ..."
npm run build

echo "Going to the dir of the data-pipelines build to create a symlink to the local repo ..."
cd "dist/data-pipelines"

echo "Link the library to local npm in order to test it ..."
npm link

echo "Going to the GUI root ..."
cd "../../"

echo "Use the local repo symlink to link it to node_modules ..."
npm link @versatiledatakit/data-pipelines

echo "Logging global npm packages"
npm ls -g

echo "Logging local npm packages"
npm ls
