# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from copy import deepcopy
from typing import Dict

from vdk.api.plugin.plugin_input import ISecretsServiceClient

log = logging.getLogger(__name__)


class InMemSecretsServiceClient(ISecretsServiceClient):
    """
    Implementation of IProperties that are kept only in memory.
    """

    def __init__(self):
        self._secrets = {}

    def read_secrets(self, job_name: str, team_name: str) -> Dict:
        res = deepcopy(self._secrets)
        return res

    def write_secrets(self, job_name: str, team_name: str, secrets: Dict) -> Dict:
        log.warning(
            "You are using In Memory Secrets client. "
            "That means the secrets will not be persisted past the Data Job run."
        )
        self._secrets = deepcopy(secrets)
        return self._secrets
