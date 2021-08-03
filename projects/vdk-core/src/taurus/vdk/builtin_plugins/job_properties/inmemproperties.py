# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from copy import deepcopy
from typing import Dict

from taurus.api.plugin.plugin_input import IPropertiesServiceClient

log = logging.getLogger(__name__)


class InMemPropertiesServiceClient(IPropertiesServiceClient):
    """
    Impelmentation of IProperties that are kept only in memory.
    """

    def __init__(self):
        self._props = {}

    def read_properties(self, job_name: str) -> Dict:
        res = deepcopy(self._props)
        return res

    def write_properties(self, job_name: str, properties: Dict) -> None:
        self._props = deepcopy(properties)
