# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus_datajob_api import ApiClient
from taurus_datajob_api import Configuration
from taurus_datajob_api import DataJobsApi
from taurus_datajob_api import DataJobsDeploymentApi
from taurus_datajob_api import DataJobsExecutionApi
from taurus_datajob_api import DataJobsPropertiesApi
from taurus_datajob_api import DataJobsSourcesApi
from urllib3 import Retry
from vdk.internal.control.auth.auth import Authentication
from vdk.internal.control.configuration.vdk_config import VDKConfig

log = logging.getLogger(__name__)


class ApiClientFactory:
    def __init__(self, rest_api_url):
        log.debug(f"Rest API URL: {rest_api_url}")
        self.vdk_config = VDKConfig()
        self.op_id = self.vdk_config.op_id
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
        api_client.set_default_header("X-OPID", self.op_id)
        self.__setup_kerberos_auth_if_necessary(api_client)
        return api_client

    def __setup_kerberos_auth_if_necessary(self, api_client: ApiClient) -> None:
        """
        We are decorating call_api as we need to be able to inject
        a newly generated (Kerberos) Authorization header on every request.
        """
        from vdk.internal.control.auth import kerberos_client

        if not kerberos_client.is_kerberos_installed():
            log.debug(
                "Kerberos is is not installed. Kerberos authentication will not be used."
            )
            return None
        if not self.vdk_config.kerberos_authentication_enabled:
            log.debug(
                "Kerberos authentication has been explicitly disabled with a flag ."
            )
            return None

        auth = Authentication()
        auth.update_kerberos_service_name(self.vdk_config.kerberos_service_name)

        def call_api_decorator(fn):
            def inner(
                self,
                resource_path,
                method,
                path_params=None,
                query_params=None,
                header_params=None,
                *args,
                **kwargs,
            ):
                auth_header = auth.read_kerberos_auth_header()
                if auth_header:
                    if header_params is None:
                        header_params = {}
                    header_params["Authorization"] = auth.read_kerberos_auth_header()
                else:
                    log.debug(
                        "Could not generate Authorization header for Kerberos (GSS Negotiate). "
                        "We will proceed with the request as normal "
                        "but if authentication is required it may fail."
                    )

                return fn(
                    resource_path,
                    method,
                    path_params,
                    query_params,
                    header_params,
                    *args,
                    **kwargs,
                )

            return inner

        api_client.call_api = call_api_decorator(api_client.call_api).__get__(
            api_client
        )

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
