#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VERSION_TAG=$(cat "$SCRIPT_DIR/version.txt")
VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}

function build_and_push_image() {
    name="$1"
    docker_file="$2"
    arguments="$3"

    image_repo="$VDK_DOCKER_REGISTRY_URL/$name"
    image_tag="$image_repo:$VERSION_TAG"

    docker build -t $image_tag -t $image_repo:latest -f "$SCRIPT_DIR/$docker_file" $arguments "$SCRIPT_DIR"
    docker_push_vdk.sh $image_tag
    docker_push_vdk.sh $image_repo:latest
}

build_and_push_image "job-builder-secure" Dockerfile
