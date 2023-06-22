#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

out=$(npm view @versatiledatakit/shared versions --json | grep $1-rc | cut -d \" -f 2 | tail -1 | awk -F '.' '{print $4}')
out=$((out+1))
echo $out
