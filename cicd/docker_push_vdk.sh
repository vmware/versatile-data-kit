#!/usr/bin/env bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# This Bash script provides a utility to push a containers image to multiple container registries.
# The scripts automatically detects if there's registry and user and ignores them using only repository and tag
# to push them to each respective registry
#
# The script uses several environment variables:
#
#   VDK_DOCKER_REGISTRY_URL: Docker registry URL for VDK Docker images.
#   VDK_DOCKER_REGISTRY_USERNAME: Username for the VDK Docker registry.
#   VDK_DOCKER_REGISTRY_PASSWORD: Password for the VDK Docker registry.
#   CICD_CONTAINER_REGISTRY_URI: Container registry URL for VDK GitHub images.
#   CICD_CONTAINER_REGISTRY_USER_NAME: Username for the VDK GitHub Container registry.
#   CICD_CONTAINER_REGISTRY_USER_PASSWORD: Password for the VDK GitHub Container registry.
#
# Those variables are set automatically in Gitlab CI environment of VDK
# See more details in https://github.com/vmware/versatile-data-kit/wiki/Gitlab-CICD#cicd-demo-installation-variables
#
# Usage:
# ./docker_push_vdk <docker_image_name>

# set -o nounset -o errexit -o pipefail



SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/docker_parse.sh"

function push_image_to_vdk_registries() {

  if [ -z "${VDK_REGISTRIES}" ]; then
      export VDK_REGISTRIES=(
        "${VDK_DOCKER_REGISTRY_URL} ${VDK_DOCKER_REGISTRY_USERNAME} ${VDK_DOCKER_REGISTRY_PASSWORD}"
        "${CICD_CONTAINER_REGISTRY_URI} ${CICD_CONTAINER_REGISTRY_USER_NAME} ${CICD_CONTAINER_REGISTRY_USER_PASSWORD}"
        )
  fi

  local DOCKER_IMAGE="$1"

  parse_docker_image "$DOCKER_IMAGE"

  echo "Discarding user and registry part of the docker image: $DOCKER_IMAGE -> $IMAGE_REPOSITORY/$IMAGE_TAG"
  local TARGET_DOCKER_IMAGE="$IMAGE_REPOSITORY:$IMAGE_TAG"

  for registry in "${VDK_REGISTRIES[@]}"; do
      REGISTRY_URL=$(echo "$registry" | awk '{print $1}')
      USERNAME=$(echo "$registry" | awk '{print $2}')
      PASSWORD=$(echo "$registry" | awk '{print $3}')

      echo "$PASSWORD" | docker login "$REGISTRY_URL" --username "$USERNAME" --password-stdin

      if [ $? -eq 0 ]; then
          # Tag the Docker image for the registry
          docker tag "$DOCKER_IMAGE" "$REGISTRY_URL/$TARGET_DOCKER_IMAGE"

          echo "docker push $REGISTRY_URL/$TARGET_DOCKER_IMAGE"
          docker push "$REGISTRY_URL/$TARGET_DOCKER_IMAGE"
      fi
  done
}

push_image_to_vdk_registries "$@"
