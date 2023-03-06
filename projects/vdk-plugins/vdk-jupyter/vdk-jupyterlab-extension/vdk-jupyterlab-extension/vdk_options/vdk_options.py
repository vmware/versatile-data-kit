# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from enum import Enum


class VdkOption(Enum):
    NAME = "jobName"
    TEAM = "jobTeam"
    REST_API_URL = "restApiUrl"
    PATH = "jobPath"
    CLOUD = "cloud"
    LOCAL = "local"
    ARGUMENTS = "jobArguments"
    VDK_VERSION = "vdkVersion"
    DEPLOYMENT_REASON = "deploymentReason"
    DEPLOY_ENABLE = "enableDeploy"

