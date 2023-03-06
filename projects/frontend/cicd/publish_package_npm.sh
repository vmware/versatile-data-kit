#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

###
# This script is purposed for publishing to https://registry.npmjs.org/ (default public repo).
# It is meant to publish the release NPM artifact of a subproject in `projects/frontend/`:
# * shared-components
# * data-pipelines
#
# Usage:
# ./publish_package_npm.sh <component> <minor_version_unique> <token> [npm_registry_optional]
# Example:
# ./publish_package_npm.sh data-pipelines 123456 npm_token registry.npmjs.org
###

if ! which npm >/dev/null 2>&1 ; then
  echo "ERROR:"
  echo "Please install npm 8.5.5+. Publish cannot continue without it."
  exit 1
fi
echo "Logging npm engines version..."
npm version

cd "$(dirname $0)" || exit 1

# Locate the projects/frontend/ subproject directory, that contains gui/
project_types=("shared-components" "data-pipelines")
if [ $# -eq 0 ]
  then
    echo "ERROR: No argument for projects/frontend/ subproject type in [${project_types[@]}] supplied."
    exit 3
fi
if [[ ! " ${project_types[@]} " =~ " $1 " ]]
  then
    echo "ERROR: '$1' argument found, expected one of projects/frontend/ subproject types [${project_types[@]}]."
    exit 3
fi
project_type=$1
cd "../$project_type/gui"

if [ $# -eq 1 ]
  then
    echo "ERROR: No argument for unique minor package version provided."
    exit 3
fi
minor_version_unique=$2

if [ $# -eq 2 ]
  then
    echo "ERROR: No argument for NPM token provided."
    exit 3
fi
npm_token=$3

# optional; defaults to registry.npmjs.org public repo
if [ $# -eq 3 ]
  then
    npm_registry="registry.npmjs.org"
  else
    npm_registry=$4
fi


# Locate the project dist directory
if [ -d "./dist/$project_type/" ]
  then
    cd "./dist/$project_type/"
  else
    project_type_dist_short=$(cut -d "-" -f1 <<< "$project_type")
    if [ -d "./dist/$project_type_dist_short/" ]
      then
        cd "./dist/$project_type_dist_short/"
      else
        echo "ERROR: project type dist '$(pwd)/dist/$project_type/' or '$(pwd)/dist/$project_type_dist_short/' directories not found."
          exit 3
    fi
fi

# Patch distribution package version
package_version=$(awk -v id=$minor_version_unique 'BEGIN { FS="."; OFS = "."; ORS = "" } { gsub("0",id,$3); print $1, $2, $3 }' ../../version.txt)
npm version "${package_version}"

# Auth with NPM registry
npm set //$npm_registry/:_authToken $npm_token

# Publish
echo "Publishing @vdk/$(basename "$PWD"):${package_version}..."
# TODO: remove --dry-run
npm publish --ignore-scripts --access public --dry-run
