# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus_datajob_api import ApiClient
from taurus_datajob_api import Configuration
from taurus_datajob_api import DataJobsApi
from taurus_datajob_api import DataJobsDeploymentApi
from taurus_datajob_api import DataJobsExecutionApi
from taurus_datajob_api import DataJobsPropertiesApi
from taurus_datajob_api import DataJobsSecretsApi
from taurus_datajob_api import DataJobsServiceApi
from taurus_datajob_api import DataJobsSourcesApi
from urllib3 import Retry
from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.plugin.control_api_auth.authentication import Authentication

log = logging.getLogger(__name__)


class ApiClientFactory:
    def __init__(self, rest_api_url):
        log.debug(f"Rest API URL: {rest_api_url}")
        self.vdk_config = VDKConfig()
        self.timeouts = (
            self.vdk_config.http_connect_timeout_seconds,
            self.vdk_config.http_read_timeout_seconds,
        )
        # Configuration there is refresh_api_key_hook which may be useful ...
        self.config = Configuration(host=rest_api_url, api_key=None)
        self.config.connection_pool_maxsize = (
            self.vdk_config.http_connection_pool_maxsize
        )
        self.config.retries = Retry(
            total=self.vdk_config.http_total_retries,
            connect=self.vdk_config.http_connect_retries,
            read=self.vdk_config.http_read_retries,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
        )
        self.config.client_side_validation = False
        self.config.verify_ssl = self.vdk_config.http_verify_ssl

        auth = Authentication()
        # For now there's no need to add auto-update since this is called usually in a shell script
        # and each command will have short execution life even when multiple requests to API are made.
        self.config.access_token = auth.read_access_token()

    def _new_api_client(self):
        api_client = ApiClient(self.config)
        # We are setting X-OPID - this is send in telemetry and printed in logs on server side - make it easier
        # to troubleshoot and trace requests across different services
        api_client.set_default_header("X-OPID", self.vdk_config.op_id)
        api_client.set_default_header("User-Agent", self.vdk_config.user_agent)
        return api_client

    def get_jobs_api(self) -> DataJobsApi:
        return DataJobsApi(self._new_api_client())

    def get_jobs_sources_api(self) -> DataJobsSourcesApi:
        return DataJobsSourcesApi(self._new_api_client())

    def get_deploy_api(self) -> DataJobsDeploymentApi:
        return DataJobsDeploymentApi(self._new_api_client())

    def get_execution_api(self) -> DataJobsExecutionApi:
        return DataJobsExecutionApi(self._new_api_client())

    def get_properties_api(self) -> DataJobsPropertiesApi:
        return DataJobsPropertiesApi(self._new_api_client())

    def get_secrets_api(self) -> DataJobsSecretsApi:
        return DataJobsSecretsApi(self._new_api_client())

    def get_service_api(self) -> DataJobsServiceApi:
        return DataJobsServiceApi(self._new_api_client())
