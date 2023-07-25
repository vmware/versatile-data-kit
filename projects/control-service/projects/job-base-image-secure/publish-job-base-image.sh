#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VERSION_TAG="${VERSION_TAG:-"0.1dev"}"
VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}

PYTHON_MAJOR=$1
PYTHON_MINOR=$2
python_name="python-$PYTHON_MAJOR.$PYTHON_MINOR-secure"
data_job_base_name="data-job-base-python-$PYTHON_MAJOR.$PYTHON_MINOR-secure"
data_job_base_docker_file="Dockerfile-data-job-base"

python_image_repo="$VDK_DOCKER_REGISTRY_URL/$python_name"
python_image_tag_latest="$python_image_repo:latest"

data_job_base_image_repo="$VDK_DOCKER_REGISTRY_URL/$data_job_base_name"
data_job_base_image_tag_local="$data_job_base_image_repo:local"
data_job_base_image_tag_version="$data_job_base_image_repo:$VERSION_TAG"
data_job_base_image_tag_latest="$data_job_base_image_repo:latest"

docker build -t "$data_job_base_image_tag_local" -f "$SCRIPT_DIR/$data_job_base_docker_file" "$SCRIPT_DIR" \
--build-arg base_image="$python_image_tag_latest"

docker_push_vdk.sh "$data_job_base_image_tag_version"
docker_push_vdk.sh "$data_job_base_image_tag_latest"
