# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from copy import deepcopy
from typing import Dict

from vdk.api.plugin.plugin_input import IPropertiesServiceClient

log = logging.getLogger(__name__)


class InMemPropertiesServiceClient(IPropertiesServiceClient):
    """
    Implementation of IProperties that are kept only in memory.
    """

    def __init__(self):
        self._props = {}

    def read_properties(self, job_name: str, team_name: str) -> Dict:
        res = deepcopy(self._props)
        return res

    def write_properties(self, job_name: str, team_name: str, properties: Dict) -> Dict:
        log.warning(
            "You are using In Memory Properties client. "
            "That means the properties will not be persisted past the Data Job run."
        )
        self._props = deepcopy(properties)
        return self._props
