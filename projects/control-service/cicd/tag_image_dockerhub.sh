#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}

[ $# -eq 0 ] && echo "ERROR: No argument for docker image name provided." && exit 1
[ $# -eq 1 ] && echo "ERROR: No argument for docker image tag." && exit 1
[ $# -eq 2 ] && echo "ERROR: No argument for docker image new tag." && exit 1


name="$1"
current_tag="$2"
new_tag="$3"

old_image="$VDK_DOCKER_REGISTRY_URL/$name:$current_tag"
new_image="$VDK_DOCKER_REGISTRY_URL/$name:$new_tag"

docker pull $old_image
docker tag $old_image $new_image
docker push $new_image
