# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from enum import Enum


class VdkOption(Enum):
    NAME = "jobName"
    TEAM = "jobTeam"
    PATH = "jobPath"
    ARGUMENTS = "jobArguments"
    DEPLOYMENT_REASON = "deploymentReason"
