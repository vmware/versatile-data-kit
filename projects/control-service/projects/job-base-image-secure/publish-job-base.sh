#!/bin/bash

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VERSION_TAG="0.1docker-slim"
VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}

function build_and_push_image() {
    name="$1"
    docker_file="$2"
    arguments="$3"

    image_repo="$VDK_DOCKER_REGISTRY_URL/$name"
    image_tag_local="$image_repo:local"
    image_tag_version="$image_repo:$VERSION_TAG"
    image_tag_latest="$image_repo:latest"

    docker build -t "$image_tag_local" -f "$SCRIPT_DIR/$docker_file" $arguments "$SCRIPT_DIR"

    docker-slim build \
    --target "$image_tag_local" \
    --tag "$image_tag_version" \
    #--tag "$image_tag_latest" \
    --http-probe=false \
    --exec "/bin/sh -c \"groupadd -h && useradd -h && pip3 list && export PYTHONPATH=/usr/local/lib/python3.7/site-packages:/vdk/site-packages/ && userdel --help && groupdel --help && chown --help && chmod --help && rm --help && python3 -m pip install --upgrade pip && /bin/bash --help\"" \
    --include-path "/usr/lib"

    docker push "$image_tag_version"
    #docker push "$image_tag_latest"
}

build_and_push_image \
    "data-job-base-python-3.10-secure" \
    Dockerfile-data-job-base
