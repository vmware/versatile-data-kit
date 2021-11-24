# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from requests.adapters import Retry
from requests.auth import AuthBase
from vdk.api.plugin.plugin_input import IPropertiesServiceClient
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.core import errors

log = logging.getLogger(__name__)


class ControlServicePropertiesServiceClient(IPropertiesServiceClient):
    """
    Implementation of PropertiesServiceClient which connects to Pipelines Control Service Properties API
    """

    def __init__(self, rest_api_url: str):
        self.__properties_api = ApiClientFactory(rest_api_url).get_properties_api()
        log.debug(f"Initialized Properties against {rest_api_url}.")

    def read_properties(self, job_name: str, team_name: str):
        data = self.__properties_api.data_job_properties_read(
            team_name=team_name, job_name=job_name, deployment_id="TODO"
        )
        return data

    def write_properties(self, job_name: str, team_name: str, properties: Dict):
        self.__properties_api.data_job_properties_update(
            team_name=team_name,
            job_name=job_name,
            deployment_id="TODO",
            request_body=properties,
        )
