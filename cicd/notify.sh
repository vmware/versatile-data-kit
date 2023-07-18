#!/bin/bash -e
# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

curl -X POST -H "Content-type: application/json" --data "{\"text\":\"$1\"}" $2
