#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Extracts the latest rc-version number for the pipeline id that's passed
# and returns the incremented version number
# e.g. if the latest rc-version is 1.3.${pipeline_id}-rc.3, the script will return 4
if [ $# -eq 0 ]
  then
    echo "ERROR: No argument for pipeline id supplied"
    exit 3
fi

out=$(npm view @versatiledatakit/shared versions --json | grep $1-rc | cut -d \" -f 2 | tail -1 | awk -F '.' '{print $4}')
out=$((out+1))
echo $out
