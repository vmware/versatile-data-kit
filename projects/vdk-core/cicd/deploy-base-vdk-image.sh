#!/usr/bin/env bash

# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0

# The script builds a docker image with fully installed VDK - native dependencies, python dependencies and the actual VDK.
# The image is then deployed to ECR with.
# This image will be used for base image for each data job.
#
# configured with environment variables:

export VDK_VERSION=${VDK_VERSION:-$(python setup.py --version)} # used to retrieve the VDK version that should be installed
export BUILD_TYPE=${BUILD_TYPE:-release} # used to tag the image, either release-candidate or release
export VDK_PACKAGE=${VDK_PACKAGE:-$(python setup.py --name)}
export VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}
export DOCKER_REGISTRY_IMAGE=${DOCKER_REGISTRY_IMAGE:-"$VDK_DOCKER_REGISTRY_URL/$VDK_PACKAGE"}  # where the image should be pushed
export PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL:-https://test.pypi.org/simple/}
export VDK_BASE_PYTHON_IMAGE=${VDK_BASE_PYTHON_IMAGE:-python:3.7-slim}

set -o errexit -o nounset

if [ -z "$VDK_VERSION" ]; then
  echo "Please specify VDK version that can be found in PIP repo: export VDK_VERSION=..."
  exit 1
fi

if [ -z "$BUILD_TYPE" ]; then
  echo "Please specify BUILD_TYPE used to tag the image, either release-candidate or release: export BUILD_TYPE=..."
  exit 1
fi

if [ -z "$DOCKER_REGISTRY_IMAGE" ]; then
  echo "Please specify DOCKER_REGISTRY_IMAGE where the image will be pushed,"
  exit 1
fi

echo "Publishing $BUILD_TYPE VDK base image with $VDK_PACKAGE version $VDK_VERSION ..."

echo "{\"auths\":{\"$VDK_DOCKER_REGISTRY_URL\":{\"username\":\"$VDK_DOCKER_REGISTRY_USERNAME\",\"password\":\"$VDK_DOCKER_REGISTRY_PASSWORD\"}}}" > /kaniko/.docker/config.json


SCRIPT_DIR=$(dirname "$0")
DOCKERFILE_PATH="$SCRIPT_DIR/Dockerfile-vdk-base"
/kaniko/executor --force --single-snapshot \
        --dockerfile="${DOCKERFILE_PATH}" \
        --destination="${DOCKER_REGISTRY_IMAGE}:${VDK_VERSION}"  \
        --destination="${DOCKER_REGISTRY_IMAGE}:${BUILD_TYPE}"  \
        --build-arg=vdk_package="${VDK_PACKAGE}"           \
        --build-arg=vdk_version="${VDK_VERSION}" \
        --build-arg=pip_extra_index_url="${PIP_EXTRA_INDEX_URL}" \
        --build-arg=vdk_base_python_image="${VDK_BASE_PYTHON_IMAGE}"
