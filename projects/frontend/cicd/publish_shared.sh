#!/bin/sh
# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

VERSION=$(awk -v id=$1 'BEGIN { FS="."; OFS = "."; ORS = "" } { gsub("0",id,$3); print $1, $2, $3 }' ./version.txt)
npm set //$2/:_authToken $3
cd "./dist/shared/"
echo "Publishing @vdk/shared@"$VERSION" to registry"
npm version $VERSION && npm publish --ignore-scripts
