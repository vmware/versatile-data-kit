#!/bin/sh
# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# TODO: replace those as env variables
aws_access_key_id=$1
aws_secret_access_key=$2
aws_region=$3
docker_registry=$4
git_username=$5
git_password=$6
git_repository=$7
registry_type=$8
registry_username=$9
registry_password=${10}

# Within this property docker config should be included to connect to the registry used to pull the image from.
# it should be prefixed with a comma
# example: ,"ghcr.io/versatile-data-kit-dev/dp/versatiledatakit":{"auth":"dmVyc2F0aWxlLWRhdGEta2l0LWRldjo8bXlUb2tlbj4="}}
extra_auth=${extra_auth:-""}
# Echo selected data to be logged
echo "AWS_REGION=$aws_region"
echo "DOCKER_REGISTRY=$docker_registry"
echo "GIT_REPOSITORY=$git_repository"
echo "REGISTRY_TYPE=$registry_type"
# We default to generic repo.
# We have special support for ECR because
# even though Kaniko supports building and pushing images to ECR
# it doesn't create repository nor do they think they should support it -
# https://github.com/GoogleContainerTools/kaniko/pull/1537
# And ECR requires for each image to create separate repository
# And ECR will not create new image repository on docker push
# So we need to do it manually.
if [ "$registry_type" = "ecr" ] || [ "$registry_type" = "ECR" ] ; then
    # Setup credentials to connect to AWS - same creds will be used by kaniko as well.
    aws configure set aws_access_key_id $aws_access_key_id
    aws configure set aws_secret_access_key $aws_secret_access_key

    # Check if aws_session_token is set and not empty.
    if [ -n "$aws_session_token" ] ; then
      aws configure set aws_session_token "$aws_session_token"
    fi
    # https://stackoverflow.com/questions/1199613/extract-filename-and-path-from-url-in-bash-script
    repository_prefix=${docker_registry#*/}
    # Create docker repository if it does not exist
    aws ecr describe-repositories --region $aws_region --repository-names $repository_prefix/${DATA_JOB_NAME} ||
        aws ecr create-repository --region $aws_region --repository-name $repository_prefix/${DATA_JOB_NAME}
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
# Clone repo into /data-jobs dir to get job's source
git_url_scheme="https"
[ "$GIT_SSL_ENABLED" = false ] && git_url_scheme="http"
git clone $git_url_scheme://$git_username:$git_password@$git_repository ./data-jobs
cd ./data-jobs
git reset --hard $GIT_COMMIT || ( echo ">data-job-not-found<" && exit 1 )
if [ ! -d ${DATA_JOB_NAME} ]; then
  echo ">data-job-not-found<"
  exit 1
fi
cd ..
# kaniko supports building directly from git repository but as we've cloned it here anyhow
# (to check if job directory exists) there's no need to.
/kaniko/executor \
        --dockerfile=/workspace/Dockerfile \
        --destination="${IMAGE_REGISTRY_PATH}/${DATA_JOB_NAME}:${GIT_COMMIT}"       \
        --build-arg=job_githash="$JOB_GITHASH"            \
        --build-arg=base_image="$BASE_IMAGE" \
        --build-arg=job_name="$JOB_NAME"     \
        --context=./data-jobs $EXTRA_ARGUMENTS
