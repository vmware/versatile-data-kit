#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0


# Extracts the latest rc-version for the pipeline id that's passed
if [ $# -eq 0 ]
  then
    echo "ERROR: No argument for pipeline id supplied"
    exit 3
fi
npm view @versatiledatakit/shared versions --json | grep $1-rc | cut -d \" -f 2 | tail -1
