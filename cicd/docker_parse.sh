#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Parses a Docker image name and extracts information such as the registry, username, repository, and tag.
#
# Upon success the function sets the following environment variables based on the input image name:
#   IMAGE_REGISTRY: The Docker image registry. If no registry is specified in the image name, this will default to docker.io.
#   IMAGE_USERNAME: The username or namespace under which the image resides. If no username is specified, this will default to an empty string.
#   IMAGE_REPOSITORY: The repository where the Docker image resides.
#   IMAGE_TAG: The tag of the Docker image. If no tag is specified, this will default to latest.

function parse_docker_image() {
  local image="$1"

  if [[ -z "$image" ]]; then
      echo "Error: No image name provided."
      return 1
  fi

  # Check if there is a registry and port number
  if [[ $image == *"/"* ]]; then
    REGISTRY=${image%%/*}
    image=${image#*/}
  else
    REGISTRY="docker.io"
  fi

  # Check if there is a tag
  if [[ $image == *":"* ]]; then
    TAG=${image##*:}
    image=${image%:*}
  else
    TAG="latest"
  fi

  # Check if there is a username
  if [[ $image == *"/"* ]]; then
    USERNAME=${image%%/*}
    REPOSITORY=${image#*/}
  else
    USERNAME=""
    REPOSITORY=$image
  fi

  export IMAGE_REGISTRY=$REGISTRY
  export IMAGE_USERNAME=$USERNAME
  export IMAGE_REPOSITORY=$REPOSITORY
  export IMAGE_TAG=$TAG
}
