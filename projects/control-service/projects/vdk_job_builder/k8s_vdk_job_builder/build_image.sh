#!/bin/sh

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# TODO: deprecate and switch with officially supported docker image builders

# Fail on any error
set -ex

# Clone job
aws_access_key_id=$1
aws_secret_access_key=$2
aws_region=$3
aws_ecr_registry=$4
git_username=$5
git_password=$6
git_repository=$7
registry_type=$8
registry_username=$9
registry_password=$10


# Defaulting to Amazon ECR in case the registry type is not set in order to not break backwards
# compatibility
# and we start to version the builder image
if [ "$registry_type" = "ecr" ] || [ "$registry_type" = "ECR" ] || [ "$registry_type" = "" ]; then
    # Docker login to ECR
    aws configure set aws_access_key_id $aws_access_key_id
    aws configure set aws_secret_access_key $aws_secret_access_key
    aws ecr get-login-password --region $aws_region | docker login --username AWS --password-stdin $aws_ecr_registry

    # https://stackoverflow.com/questions/1199613/extract-filename-and-path-from-url-in-bash-script
    repository_prefix=${aws_ecr_registry#*/}
    # Create docker repository if it does not exist
    aws ecr describe-repositories --region $aws_region --repository-names $repository_prefix/${DATA_JOB_NAME} ||
        aws ecr create-repository --region $aws_region --repository-name $repository_prefix/${DATA_JOB_NAME}
elif [ "$registry_type" = "generic" ] || [ "$registry_type" = "GENERIC" ]; then
    echo -n "$registry_password" | docker login $IMAGE_REGISTRY_PATH --username $registry_username --password-stdin
fi

# Clone repo into /data-jobs dir to get job's source
git clone https://$git_username:$git_password@$git_repository /data-jobs
cd /data-jobs
git reset --hard $GIT_COMMIT || ( echo ">data-job-not-found<" && exit 1 )
if [ ! -d ${DATA_JOB_NAME} ]; then
  echo ">data-job-not-found<"
  exit 1
fi
cd ..

python3 cli.py $DATA_JOB_NAME ./vdk_job_builder/Dockerfile /data-jobs

docker push ${IMAGE_REGISTRY_PATH}/${DATA_JOB_NAME}:${GIT_COMMIT}
