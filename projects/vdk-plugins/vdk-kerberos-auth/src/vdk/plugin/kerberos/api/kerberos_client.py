# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Optional


class KerberosClient:
    """
    Use this class to access prepared Kerberos Negotate header that can be used in HTTP API requests.
    It's expected to be set as an "Authorization header"
    Example usage

    auth = KerberosClient("HTTP@vdk.fqdn.com")
    api_call_headers["Authorization"] = auth.read_kerberos_auth_header()
    """

    def __init__(self, api_server_kerberos_service_name: str):
        """
        :param api_server_kerberos_service_name: the kerberos service name of the API Server we want to connect to.
        """
        self.__kerberos_service_name = api_server_kerberos_service_name

    def acquire_kerberos_auth_header(self) -> Optional[str]:
        """
        Return the header to be used by API requests to server supporting kerberos authentication.
        You can see more details here http://python-notes.curiousefficiency.org/en/latest/python_kerberos.html
        :return:
        """
        if self.__kerberos_service_name:
            from vdk.plugin.kerberos.kerberos_ticket import KerberosTicket

            client = KerberosTicket(self.__kerberos_service_name)
            return client.auth_header
        return None
