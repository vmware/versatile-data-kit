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
    data_job_base_name="data-job-base-python-$PYTHON_MAJOR.$PYTHON_MINOR-secure"
    python_docker_file="Dockerfile-python"
    data_job_base_docker_file="Dockerfile-data-job-base"

    python_image_repo="$VDK_DOCKER_REGISTRY_URL/$python_name"
    python_image_tag_local="$python_image_repo:local"
    python_image_tag_version="$python_image_repo:$VERSION_TAG"
    python_image_tag_latest="$python_image_repo:latest"

    data_job_base_image_repo="$VDK_DOCKER_REGISTRY_URL/$data_job_base_name"
    data_job_base_image_tag_local="$data_job_base_image_repo:local"
    data_job_base_image_tag_version="$data_job_base_image_repo:$VERSION_TAG"
    data_job_base_image_tag_latest="$data_job_base_image_repo:latest"

    docker build -t "$python_image_tag_local" -t "$python_image_tag_version" -t "$python_image_tag_latest" -f "$SCRIPT_DIR/$python_docker_file" "$SCRIPT_DIR" \
    --build-arg PYTHON_MAJOR=$PYTHON_MAJOR \
    --build-arg PYTHON_MINOR=$PYTHON_MINOR \
    --build-arg PYTHON_PATCH=$PYTHON_PATCH

    docker push "$python_image_tag_version"
    docker push "$python_image_tag_latest"

    docker build -t "$data_job_base_image_tag_local" -f "$SCRIPT_DIR/$data_job_base_docker_file" "$SCRIPT_DIR" \
    --build-arg base_image=$python_image_tag_version

    docker-slim build \
    --target "$data_job_base_image_tag_local" \
    --tag "$data_job_base_image_tag_version" \
    --tag "$data_job_base_image_tag_latest" \
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

    docker push "$data_job_base_image_tag_version"
    docker push "$data_job_base_image_tag_latest"
}

build_and_push_image 3 8 16

build_and_push_image 3 9 16

build_and_push_image 3 10 11

build_and_push_image 3 11 3
