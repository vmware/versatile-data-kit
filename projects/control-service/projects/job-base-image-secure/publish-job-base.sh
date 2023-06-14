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
    name="data-job-base-python-$PYTHON_MAJOR.$PYTHON_MINOR-secure"
    docker_file="Dockerfile-data-job-base"

    image_repo="$VDK_DOCKER_REGISTRY_URL/$name"
    image_tag_local="$image_repo:local"
    image_tag_version="$image_repo:$VERSION_TAG"
    image_tag_latest="$image_repo:latest"

    docker build -t "$image_tag_local" -f "$SCRIPT_DIR/$docker_file" "$SCRIPT_DIR" \
    --build-arg PYTHON_MAJOR=$PYTHON_MAJOR \
    --build-arg PYTHON_MINOR=$PYTHON_MINOR \
    --build-arg PYTHON_PATCH=$PYTHON_PATCH

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
    --include-path "/usr/lib" \
    --include-path "/usr/local/lib/python$PYTHON_MAJOR.$PYTHON_MINOR/"


    docker push "$image_tag_version"
    docker push "$image_tag_latest"
}

build_and_push_image 3 8 16

build_and_push_image 3 9 16

build_and_push_image 3 10 11

build_and_push_image 3 11 3
