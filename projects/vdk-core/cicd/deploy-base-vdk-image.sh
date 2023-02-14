#!/usr/bin/env bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
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


docker login --username "${VDK_DOCKER_REGISTRY_USERNAME}" --password "${VDK_DOCKER_REGISTRY_PASSWORD}" "${DOCKER_REGISTRY_IMAGE}"

SCRIPT_DIR=$(dirname "$0")
DOCKERFILE_PATH="$SCRIPT_DIR/Dockerfile-vdk-base"
docker build  -t "${DOCKER_REGISTRY_IMAGE}:${BUILD_TYPE}" -t "${DOCKER_REGISTRY_IMAGE}:${VDK_VERSION}" \
  --label "vdk_version=${VDK_VERSION}" \
  --no-cache --force-rm \
  --file "${DOCKERFILE_PATH}" \
  --build-arg vdk_package="${VDK_PACKAGE}" \
  --build-arg vdk_version="${VDK_VERSION}" \
  --build-arg pip_extra_index_url="${PIP_EXTRA_INDEX_URL}" \
  .

# docker registry must allow override
docker push "${DOCKER_REGISTRY_IMAGE}:${BUILD_TYPE}"
docker push "${DOCKER_REGISTRY_IMAGE}:${VDK_VERSION}"
