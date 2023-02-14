# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict

from vdk.api.plugin.plugin_input import IPropertiesServiceClient
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from vdk.plugin.control_cli_plugin.control_service_api_error_decorator import (
    ConstrolServiceApiErrorDecorator,
)

log = logging.getLogger(__name__)


class ControlServicePropertiesServiceClient(IPropertiesServiceClient):
    """Implementation of PropertiesServiceClient which connects to VDK Control
    Service Properties API."""

    def __init__(self, rest_api_url: str):
        self.__properties_api = ApiClientFactory(rest_api_url).get_properties_api()
        log.debug(f"Initialized Properties against {rest_api_url}.")

    @ConstrolServiceApiErrorDecorator()
    def read_properties(self, job_name: str, team_name: str):
        data = self.__properties_api.data_job_properties_read(
            team_name=team_name, job_name=job_name, deployment_id="TODO"
        )
        return data

    @ConstrolServiceApiErrorDecorator()
    def write_properties(self, job_name: str, team_name: str, properties: Dict) -> Dict:
        self.__properties_api.data_job_properties_update(
            team_name=team_name,
            job_name=job_name,
            deployment_id="TODO",
            request_body=properties,
        )
        return properties
