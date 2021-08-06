#!/bin/bash -e

# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

cd "$(dirname $0)" || exit 1
cd ..

export TAG=${TAG:-$(git rev-parse --short HEAD)}

./projects/gradlew -p ./projects/model build publishToMavenLocal --info --stacktrace
./projects/gradlew -p ./projects build jacocoTestReport -x integrationTest --info --stacktrace
./projects/gradlew -p ./projects :pipelines_control_service:docker --info --stacktrace -Pversion=$TAG
