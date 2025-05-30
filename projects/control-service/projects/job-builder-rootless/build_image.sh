#!/bin/sh
# Copyright 2023-2025 Broadcom
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
aws_session_token=${11}

# Echo selected data to be logged
echo "AWS_REGION=$aws_region"
echo "DOCKER_REGISTRY=$docker_registry"
echo "GIT_REPOSITORY=$git_repository"
echo "REGISTRY_TYPE=$registry_type"
mkdir /home/user/.docker
# We default to generic repo.
# We have special support for ECR because
# ECR requires for each image to create separate repository
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
    echo '{ "credsStore": "ecr-login" }' > ~/.docker/config.json
elif [ "$registry_type" = "generic" ] || [ "$registry_type" = "GENERIC" ] || [ "$registry_type" = "jfrog" ] || [ "$registry_type" = "JFROG" ]; then
    export auth=$(echo -n $registry_username:$registry_password | base64 -w 0)
cat > ~/.docker/config.json <<- EOM
{
  "auths": {
    "$IMAGE_REGISTRY_PATH": {
      "username":"$registry_username",
      "password":"$registry_password",
      "auth": "$auth"
    }
  }
}
EOM
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
rootlesskit buildctl-daemonless.sh build \
                             --frontend \
                             dockerfile.v0 \
                             --local context=./data-jobs \
                             --local dockerfile=./ \
                             --opt filename=./Dockerfile \
                             --opt build-arg:job_githash="$JOB_GITHASH" \
                             --opt build-arg:base_image="$BASE_IMAGE" \
                             --opt build-arg:job_name="$JOB_NAME" \
                             --output "type=image,name=${IMAGE_REGISTRY_PATH}/${DATA_JOB_NAME}:${GIT_COMMIT},push=true"
