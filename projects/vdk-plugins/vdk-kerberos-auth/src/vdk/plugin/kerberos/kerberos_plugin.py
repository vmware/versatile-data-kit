# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.core import errors
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.kerberos.kinit_authenticator import KinitGSSAPIAuthenticator
from vdk.plugin.kerberos.minikerberos_authenticator import (
    MinikerberosGSSAPIAuthenticator,
)


KRB_AUTH = "KRB_AUTH"
KEYTAB_FOLDER = "KEYTAB_FOLDER"
KEYTAB_FILENAME = "KEYTAB_FILENAME"
KEYTAB_PRINCIPAL = "KEYTAB_PRINCIPAL"
KEYTAB_REALM = "KEYTAB_REALM"
KERBEROS_KDC_HOST = "KERBEROS_KDC_HOST"


class KerberosPlugin:
    def __init__(self):
        self._log = logging.getLogger(__name__)
        self._authenticator = None

    def get_authenticator(self, context: JobContext):
        if self._authenticator is None:
            configuration = context.core_context.configuration
            keytab_pathname, keytab_principal, keytab_realm = self.__get_keytab_info(
                context
            )
            try:
                krb_auth = configuration.get_value(KRB_AUTH)
                if krb_auth == "minikerberos":
                    self._authenticator = MinikerberosGSSAPIAuthenticator(
                        keytab_pathname,
                        keytab_principal,
                        keytab_realm,
                        configuration.get_value(KERBEROS_KDC_HOST),
                    )
                elif krb_auth == "kinit":
                    self._authenticator = KinitGSSAPIAuthenticator(
                        keytab_pathname,
                        keytab_principal,
                    )  # Can kinit the whole process
                elif krb_auth is None:
                    self._log.debug("No Kerberos authentication specified")
                else:
                    errors.log_and_throw(
                        to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                        log=self._log,
                        what_happened=f"Provided environment variable {'VDK_KRB_AUTH'} has invalid value.",
                        why_it_happened=f"VDK was run with environment variable {'VDK_KRB_AUTH'}={krb_auth}, "
                        f"however '{krb_auth}' is invalid value for this variable.",
                        consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                        countermeasures=f"Provide either 'minikerberos' or 'kinit' for environment variable {'VDK_KRB_AUTH'}.",
                    )
            except VDKException:
                self._log.debug(
                    f"Kerberos authenticator cannot be created. You can provide configuration that specifies "
                    f"keytab info using the following environment variables: {'VDK_KEYTAB_FOLDER'}, or "
                    f"{'VDK_KEYTAB_FILENAME'} and {'VDK_KEYTAB_PRINCIPAL'}"
                )
                self._authenticator = None
        return self._authenticator

    @staticmethod
    def __get_keytab_info(context: JobContext):
        configuration = context.core_context.configuration
        job_name = context.name
        job_directory = str(context.job_directory)
        keytab_folder = configuration.get_value(KEYTAB_FOLDER)
        if keytab_folder is None:
            keytab_folder = job_directory
        keytab_principal = configuration.get_value(KEYTAB_PRINCIPAL)
        if keytab_principal is None:
            keytab_principal = f"pa__view_{job_name}"
        keytab_filename = configuration.get_value(KEYTAB_FILENAME)
        if keytab_filename is None:
            keytab_filename = f"{job_name}.keytab"
        keytab_pathname = os.path.join(keytab_folder, keytab_filename)
        keytab_realm = configuration.get_value(KEYTAB_REALM)
        return keytab_pathname, keytab_principal, keytab_realm


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for Kerberos with reasonable defaults
    """
    config_builder.add(
        key=KRB_AUTH,
        default_value=None,
    )
    config_builder.add(
        key=KEYTAB_FILENAME,
        default_value=None,
    )
    config_builder.add(
        key=KEYTAB_PRINCIPAL,
        default_value=None,
    )
    config_builder.add(
        key=KEYTAB_REALM,
        default_value="localhost",
    )
    config_builder.add(
        key=KERBEROS_KDC_HOST,
        default_value="localhost",
    )


@hookimpl(tryfirst=True)
def initialize_job(context: JobContext) -> None:
    _authenticator = KerberosPlugin().get_authenticator(context)
    if _authenticator:
        _authenticator.authenticate()
