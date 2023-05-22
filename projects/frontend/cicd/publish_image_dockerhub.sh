#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}

[ $# -eq 0 ] && echo "ERROR: No argument for docker image name provided." && exit 1
[ $# -eq 1 ] && echo "ERROR: No argument for UI project path provided." && exit 1
[ $# -eq 2 ] && echo "ERROR: No argument for unique patch version provided." && exit 1

name="$1"
ui_path="$2"
patch_version="$3"

[ ! -d "$ui_path/dist/ui" ] && echo "ERROR: dist/ui directory does not exist under path $ui_path" && exit 1

version_tag=$(awk -v id=$patch_version 'BEGIN { FS="."; OFS = "."; ORS = "" } { gsub("0",id,$3); print $1, $2, $3 }' $ui_path/version.txt)

image_repo="$VDK_DOCKER_REGISTRY_URL/$name"
image_tag="$image_repo:$version_tag"
commit_sha=$(git rev-parse --short HEAD)

docker build -t "$image_tag" -t "$image_repo:latest" -t "$image_repo:$commit_sha" $ui_path
docker push "$image_tag"
docker push "$image_repo:latest"
docker push "$image_repo:$commit_sha"
