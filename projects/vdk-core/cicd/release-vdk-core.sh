#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

cd "$(dirname $0)" || exit 1
cd ..


build_info_file="src/vdk/internal/vdk_build_info.py"
echo "" > $build_info_file # clear build info file first

echo "RELEASE_VERSION='$(cat version.txt)'" >> $build_info_file
echo "BUILD_DATE='$(date -u)'" >> $build_info_file
echo "BUILD_MACHINE_INFO='$(uname -a)'" >> $build_info_file

echo "GITLAB_CI_JOB_ID='$CI_JOB_ID'" >> $build_info_file

if [ -z "$CI_COMMIT_SHA" ]; then
  echo "GIT_COMMIT_SHA='$(git rev-parse HEAD)'" >> $build_info_file
  echo "GIT_BRANCH='$(git branch --show-current)'" >> $build_info_file
else
  echo "GIT_COMMIT_SHA='$CI_COMMIT_SHA'" >> $build_info_file
  echo "GIT_BRANCH='$CI_COMMIT_REF_NAME'" >> $build_info_file
fi

pip install -U pip setuptools wheel twine
python setup.py sdist --formats=gztar
# provide credentials as Gitlab variables
twine upload --repository-url $PIP_REPO_UPLOAD_URL -u "$PIP_REPO_UPLOAD_USER_NAME" -p "$PIP_REPO_UPLOAD_USER_PASSWORD" dist/*tar.gz --verbose
