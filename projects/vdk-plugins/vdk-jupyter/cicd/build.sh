#!/usr/bin/env bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

set -eou pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXT_DIR="$SCRIPT_DIR/../vdk-jupyterlab-extension"


function check_command() {
  local cmd="$1"
  local doc="$2"
  if ! command -v "$cmd" &> /dev/null; then
          echo "Error: $cmd is not installed or not in the system PATH." >&2
          echo "To install $cmd, refer to the official documentation:" >&2
          echo "$doc" >&2
          exit 1
  fi
}

check_command "npm" "https://docs.npmjs.com/downloading-and-installing-node-js-and-npm"
check_command "pip" "https://pip.pypa.io/en/stable/installation"

cd "$EXT_DIR" || { echo "Error: Could not change to directory $EXT_DIR" >&2; exit 1; }

echo "Building vdk-jupyterlab-extension"

echo "Run npm ci command to install the versions of the dependencies specified in the package-lock.json"
npm ci
echo "Upgrade pip"
pip install -U pip
echo "Install python package in development mode"
pip install -e .
echo "Link the development version of the extension with JupyterLab"
jupyter labextension develop . --overwrite
echo "Install JupyterLab server extension in develop mode"
jupyter server extension enable vdk-jupyterlab-extension
echo "Build JavaScript assets for the JupyterLab extension"
jlpm build

echo "Notes:"
echo "Rebuild extension Typescript source after making changes using  jlpm build  or start  jlpm watch  to track and rebuild automatically"

echo "Start jupyter server using"
echo "jupyter lab"
