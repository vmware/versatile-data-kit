#!/bin/bash -e
# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

curl -X POST -H "Content-type: application/json" --data "{\"text\":\"$1\"}" $2
