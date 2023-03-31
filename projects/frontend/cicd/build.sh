#!/bin/bash -e

# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_COMPONENTS_DIR="$SCRIPT_DIR/../shared-components/gui"
DATA_PIPELINES_DIR="$SCRIPT_DIR/../data-pipelines/gui"



pushd "$DATA_PIPELINES_DIR" || exit 1

echo "Installing shared-components dependencies..."
../../cicd/install_shared.sh

popd || exit 1

pushd "$SHARED_COMPONENTS_DIR" || exit 1

echo "Installing data-pipelines dependencies..."
../../cicd/install_data_pipelines.sh

popd || exit 1
