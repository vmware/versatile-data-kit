# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass
from enum import Enum


class JobProperties(Enum):
    name = "jobName"
    team = "jobTeam"
    restApiUrl = "restApiUrl"
    path = "jobPath"
    cloud = "cloud"
    local = "local"
    arguments = "jobArguments"
