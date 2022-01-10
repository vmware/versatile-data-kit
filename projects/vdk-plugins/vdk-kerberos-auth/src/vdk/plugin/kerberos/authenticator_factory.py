# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Optional

from vdk.internal.core import errors
from vdk.plugin.kerberos.base_authenticator import BaseAuthenticator
from vdk.plugin.kerberos.kerberos_configuration import KerberosPluginConfiguration
from vdk.plugin.kerberos.kinit_authenticator import KinitGSSAPIAuthenticator
from vdk.plugin.kerberos.minikerberos_authenticator import (
    MinikerberosGSSAPIAuthenticator,
)

log = logging.getLogger(__name__)


class KerberosAuthenticatorFactory:
    def __init__(self, configuration: KerberosPluginConfiguration):
        self.__configuration = configuration

    def create_authenticator(
        self, authentication_type: str
    ) -> Optional[BaseAuthenticator]:
        if authentication_type == "minikerberos":
            return MinikerberosGSSAPIAuthenticator(
                self.__configuration.krb5_conf_filename(),
                self.__configuration.keytab_pathname(),
                self.__configuration.keytab_principal(),
                self.__configuration.keytab_realm(),
                self.__configuration.kerberos_host(),
            )
        elif authentication_type == "kinit":
            return KinitGSSAPIAuthenticator(
                self.__configuration.krb5_conf_filename(),
                self.__configuration.keytab_pathname(),
                self.__configuration.keytab_principal(),
            )  # Can kinit the whole process
        elif authentication_type is None:
            log.debug("No Kerberos authentication specified")
            return None

        errors.log_and_throw(
            to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
            log=log,
            what_happened="Provided environment variable VDK_KRB_AUTH has invalid value.",
            why_it_happened=f"VDK was run with environment variable VDK_KRB_AUTH={authentication_type}, "
            f"however '{authentication_type}' is invalid value for this variable.",
            consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
            countermeasures="Provide either 'minikerberos' or 'kinit' for environment variable VDK_KRB_AUTH.",
        )
