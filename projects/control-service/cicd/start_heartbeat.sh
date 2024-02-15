#!/bin/bash

# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

VDK_HEARTBEAT_VDK_DISTRIBUTION_NAME=${VDK_HEARTBEAT_VDK_DISTRIBUTION_NAME:-'quickstart-vdk'}
VDK_HEARTBEAT_PIP_EXTRA_INDEX_URL=${VDK_HEARTBEAT_PIP_EXTRA_INDEX_URL:-'https://pypi.org/simple'}

pip install --upgrade-strategy eager -U $VDK_HEARTBEAT_VDK_DISTRIBUTION_NAME --extra-index-url $VDK_HEARTBEAT_PIP_EXTRA_INDEX_URL

vdk-heartbeat -f $1
