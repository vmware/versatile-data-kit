#!/bin/sh
# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# TODO: replace those as env variables
aws_access_key_id=$1
aws_secret_access_key=$2
aws_region=$3
docker_registry=$4
export GIT_USERNAME="$5"
export GIT_PASSWORD="$6"
git_repository=$7
registry_type=$8
registry_username=$9
registry_password=${10}
aws_session_token=${11}

# Within this property docker config should be included to connect to the registry used to pull the image from.
# it should be prefixed with a comma
# example: ,"ghcr.io/versatile-data-kit-dev/dp/versatiledatakit":{"auth":"dmVyc2F0aWxlLWRhdGEta2l0LWRldjo8bXlUb2tlbj4="}}
extra_auth=${extra_auth:-""}
# Echo selected data to be logged
echo "AWS_REGION=$aws_region"
echo "DOCKER_REGISTRY=$docker_registry"
echo "GIT_REPOSITORY=$git_repository"
echo "REGISTRY_TYPE=$registry_type"

GIT_BRANCH=${GIT_BRANCH:-"master"}

# The ECR repository must have been created before calling this script
# Or the image push will fail
if [ "$registry_type" = "ecr" ] || [ "$registry_type" = "ECR" ] ; then
    # Setup credentials to connect to AWS - same creds will be used by kaniko as well.
    export AWS_ACCESS_KEY_ID="$aws_access_key_id"
    export AWS_SECRET_ACCESS_KEY="$aws_secret_access_key"

    # Check if aws_session_token is set and not empty.
    if [ -n "$aws_session_token" ] ; then
      export AWS_SESSION_TOKEN="$aws_session_token"
    fi
    echo '{ "credsStore": "ecr-login" }' > /kaniko/.docker/config.json
elif [ "$registry_type" = "generic" ] || [ "$registry_type" = "GENERIC" ]; then
    export auth=$(echo -n $registry_username:$registry_password | base64 -w 0)
cat > /kaniko/.docker/config.json <<- EOM
{
  "auths": {
    "$IMAGE_REGISTRY_PATH": {
      "username":"$registry_username",
      "password":"$registry_password",
      "auth": "$auth"
    }
  $extra_auth
  }
}
EOM
#cat /kaniko/.docker/config.json
fi

export GIT_URL="git://$git_repository#refs/heads/$GIT_BRANCH#$GIT_COMMIT"
echo "GIT_URL is $GIT_URL"

/kaniko/executor --log-timestamp=true --single-snapshot \
        --dockerfile=/workspace/Dockerfile \
        --destination="${IMAGE_REGISTRY_PATH}/${DATA_JOB_NAME}:${GIT_COMMIT}"       \
        --build-arg=job_githash="$JOB_GITHASH"            \
        --build-arg=base_image="$BASE_IMAGE" \
        --build-arg=job_name="$JOB_NAME"     \
        --context="$GIT_URL" $EXTRA_ARGUMENTS

# Hint: nice EXTRA_ARGUMENTS for kaniko when debugging are --verbosity=debug or --verbosity=trace
