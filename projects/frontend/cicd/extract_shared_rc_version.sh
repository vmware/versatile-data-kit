#!/bin/bash -e

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

npm view @versatiledatakit/shared versions --json | grep $1-rc | cut -d \" -f 2 | tail -1
