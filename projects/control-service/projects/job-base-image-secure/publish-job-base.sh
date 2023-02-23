#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VERSION_TAG="${VERSION_TAG:-"0.1dev"}"
VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}

function build_and_push_image() {
    name="$1"
    docker_file="$2"

    image_repo="$VDK_DOCKER_REGISTRY_URL/$name"
    image_tag_local="$image_repo:local"
    image_tag_version="$image_repo:$VERSION_TAG"
    image_tag_latest="$image_repo:latest"

    docker build -t "$image_tag_local" -f "$SCRIPT_DIR/$docker_file" "$SCRIPT_DIR"

    docker-slim build \
    --target "$image_tag_local" \
    --tag "$image_tag_version" \
    --tag "$image_tag_latest" \
    --http-probe=false \
    --exec "/bin/sh -c \"pip3 list && python3 -m pip install --upgrade pip\"" \
    --include-bin "/usr/bin/chmod" \
    --include-bin "/usr/bin/chown" \
    --include-bin "/usr/bin/rm" \
    --include-bin "/usr/bin/bash" \
    --include-bin "/usr/sbin/groupadd" \
    --include-bin "/usr/sbin/groupdel" \
    --include-bin "/usr/sbin/useradd" \
    --include-bin "/usr/sbin/userdel" \
    --include-path "/usr/lib"

    docker push "$image_tag_version"
    docker push "$image_tag_latest"
}

build_and_push_image \
    "data-job-base-python-3.10-secure" \
    Dockerfile-data-job-base
