#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

cd "$(dirname $0)" || exit 1
cd ..


if ! which docker >/dev/null 2>&1 ; then
  echo "WARNING:"
  echo "  Did not detect docker installed on PATH."
  echo "  Please install Docker. It is used to create Control Service container image."
  echo "  If you are new to Docker see:"
  echo "    - https://docs.docker.com/engine/install"
  echo ""
fi

if ! which java >/dev/null 2>&1 && [ -z "$JAVA_HOME" ]; then
  echo "ERROR:"
  echo "  Did not detect java installed on PATH, nor JAVA_HOME environment variable."
  echo "  Please install Java 11 JDK and/or set JAVA_HOME. You will need this in control-service project."
  echo "  If you are new to Java we recommend using Open JDK:"
  echo "    - https://openjdk.java.net/install"
  echo ""
  exit 1
fi


export TAG=${TAG:-$(git rev-parse --short HEAD)}

set -x
./projects/gradlew -p ./projects/model build publishToMavenLocal --info --stacktrace
./projects/gradlew -p ./projects build jacocoTestReport -x integrationTest --info --stacktrace
./projects/gradlew -p ./projects :pipelines_control_service:docker --info --stacktrace -Pversion=$TAG
