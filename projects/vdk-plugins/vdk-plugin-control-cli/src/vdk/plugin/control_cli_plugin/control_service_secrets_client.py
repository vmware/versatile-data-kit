# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict

from vdk.api.plugin.plugin_input import ISecretsServiceClient
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.plugin.control_cli_plugin.control_service_api_error_decorator import (
    ConstrolServiceApiErrorDecorator,
)

log = logging.getLogger(__name__)


class ControlServiceSecretsServiceClient(ISecretsServiceClient):
    """Implementation of SecretsServiceClient which connects to VDK Control
    Service Secrets API."""

    def __init__(self, rest_api_url: str):
        self.__secrets_api = ApiClientFactory(rest_api_url).get_secrets_api()
        log.debug(f"Initialized Secrets against {rest_api_url}.")

    @ConstrolServiceApiErrorDecorator()
    def read_secrets(self, job_name: str, team_name: str):
        data = self.__secrets_api.data_job_secrets_read(
            team_name=team_name, job_name=job_name, deployment_id="TODO"
        )
        return data

    @ConstrolServiceApiErrorDecorator()
    def write_secrets(self, job_name: str, team_name: str, secrets: Dict) -> Dict:
        self.__secrets_api.data_job_secrets_update(
            team_name=team_name,
            job_name=job_name,
            deployment_id="TODO",
            request_body=secrets,
        )
        return secrets
