#!/bin/bash

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VERSION_TAG=3.0.3
VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"ghcr.io/versatile-data-kit-dev/dp/versatiledatakit"}

function build_and_push_image() {
    name="$1"
    docker_file="$2"
    arguments="$3"

    image_repo="$VDK_DOCKER_REGISTRY_URL/$name"
    image_tag="$image_repo:$VERSION_TAG"

    docker buildx build --platform linux/amd64,linux/arm64 -t $image_tag -t $image_repo:latest -f "$SCRIPT_DIR/$docker_file" $arguments "$SCRIPT_DIR" --push
}

build_and_push_image "job-builder-test" Dockerfile
