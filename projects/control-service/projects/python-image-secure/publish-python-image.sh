#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VERSION_TAG="${VERSION_TAG:-"0.1dev"}"
VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}

function build_and_push_image() {
    PYTHON_MAJOR=$1
    PYTHON_MINOR=$2
    PYTHON_PATCH=$3
    python_name="python-$PYTHON_MAJOR.$PYTHON_MINOR-secure"
    python_docker_file="Dockerfile-python"

    python_image_repo="$VDK_DOCKER_REGISTRY_URL/$python_name"
    python_image_tag_version="$python_image_repo:$VERSION_TAG"
    python_image_tag_latest="$python_image_repo:latest"

    docker build -t "$python_image_tag_version" -t "$python_image_tag_latest" -f "$SCRIPT_DIR/$python_docker_file" "$SCRIPT_DIR" \
    --build-arg PYTHON_MAJOR=$PYTHON_MAJOR \
    --build-arg PYTHON_MINOR=$PYTHON_MINOR \
    --build-arg PYTHON_PATCH=$PYTHON_PATCH

    docker push "$python_image_tag_version"
    docker push "$python_image_tag_latest"
}
