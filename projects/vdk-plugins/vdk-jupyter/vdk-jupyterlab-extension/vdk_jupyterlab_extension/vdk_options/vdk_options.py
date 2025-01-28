# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from enum import Enum


class VdkOption(Enum):
    NAME = "jobName"
    TEAM = "jobTeam"
    PATH = "jobPath"
    ARGUMENTS = "jobArguments"
    DEPLOYMENT_REASON = "deploymentReason"
