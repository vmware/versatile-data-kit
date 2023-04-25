#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

###
# For installing the build prerequisites, consider `install_data_pipelines.sh` script.
# To rebuild, link and run unit tests, consider `build_data_pipelines.sh`.
# This script is meant to run the e2e tests of data-pipelines component.
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

if [ $# -eq 0 ]
  then
    echo "ERROR: No OAuth2 token provided."
    exit 3
fi
export OAUTH2_API_TOKEN="$1"
export CYPRESS_test_environment="$2"
export CYPRESS_test_guid="$3"
export CYPRESS_grepTags="$4"

echo "Starting server and running e2e tests..."
npm run start-server-and-test-e2e
