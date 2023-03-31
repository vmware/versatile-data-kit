#!/bin/bash -e
# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

echo "Logging npm engines version..."
npm version
echo "Installing dependencies..."
NODE_OPTIONS=--max_old_space_size=1000
npm install
echo "Building package..."
npm run build
echo "Linking package..."
cd dist/shared/
npm link
cd ../../
npm link @versatiledatakit/shared
echo "Starting unit tests..."
npm run test:headless
