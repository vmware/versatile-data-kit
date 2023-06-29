#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VERSION_TAG="${VERSION_TAG:-"0.1dev"}"
VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}

function build_and_push_image() {
    name="$1"
    docker_file="$2"
    arguments="$3"

    image_repo="$VDK_DOCKER_REGISTRY_URL/$name"
    image_tag="$image_repo:$VERSION_TAG"

    docker build -t "$image_tag" -t "$image_repo:latest" -f "$SCRIPT_DIR/$docker_file" $arguments "$SCRIPT_DIR"
    docker push "$image_tag"
    docker push "$image_repo:latest"
}

build_and_push_image \
    "data-job-base-torch-huggingface-python-3.7" \
    Dockerfile-data-job-base \
    "--build-arg base_image=python:3.7-slim"

build_and_push_image \
    "data-job-base-torch-huggingface-python-3.8" \
    Dockerfile-data-job-base \
    "--build-arg base_image=python:3.8-slim"

build_and_push_image \
    "data-job-base-torch-huggingface-python-3.9" \
    Dockerfile-data-job-base \
    "--build-arg base_image=python:3.9-slim"

build_and_push_image \
    "data-job-base-torch-huggingface-python-3.10" \
    Dockerfile-data-job-base \
    "--build-arg base_image=python:3.10-slim"

build_and_push_image \
    "data-job-base-torch-huggingface-python-3.11" \
    Dockerfile-data-job-base \
    "--build-arg base_image=python:3.11-slim"
