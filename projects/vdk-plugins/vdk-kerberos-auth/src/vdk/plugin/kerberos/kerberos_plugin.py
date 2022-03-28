# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.plugin.kerberos.authenticator_factory import KerberosAuthenticatorFactory
from vdk.plugin.kerberos.kerberos_configuration import add_definitions
from vdk.plugin.kerberos.kerberos_configuration import KerberosPluginConfiguration

log = logging.getLogger(__name__)


class KerberosPlugin:
    def __init__(self):
        self.__authenticator = None

    def __attempt_kerberos_authentication(
        self, kerberos_configuration: KerberosPluginConfiguration
    ):
        authenticator_factory = KerberosAuthenticatorFactory(kerberos_configuration)
        if kerberos_configuration.authentication_type() is not None:
            log.debug("Creating authenticator for Kerberos and will kinit now.")
            try:
                self.__authenticator = authenticator_factory.create_authenticator(
                    kerberos_configuration.authentication_type()
                )
                self.__authenticator.authenticate()
            except Exception as e:
                if kerberos_configuration.auth_fail_fast():
                    raise
                else:
                    log.warning(
                        "Kerberos was enabled but we failed to authenticate (kinit) and generate TGT."
                        f"The error was: {e} "
                        "This means potential future operations requiring "
                        "valid kerberos authentication will fail. "
                        "You may need to inspect the above error and try to fix it if that happens. "
                        "If no kerberos related operations are done, ignore this warning."
                        "If you prefer to fail fast (instead of this warning), enable krb_auth_fail_fast flag."
                        "See vdk config-help for more information."
                    )
        else:
            log.debug(
                "no authentication for kerberos is attempted as it's not enabled."
                "To enable set KRB_AUTH to the correct type. See vdk config-help for more infofrmation."
            )

    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder)

    @hookimpl
    def vdk_initialize(self, context: CoreContext) -> None:
        kerberos_configuration = KerberosPluginConfiguration(
            None, None, context.configuration
        )
        if (
            kerberos_configuration.keytab_filename()
            and kerberos_configuration.keytab_principal()
        ):
            self.__attempt_kerberos_authentication(kerberos_configuration)
        else:
            log.debug(
                "No keytab configuration found. "
                "No attempt for kerberos authentication is done during vdk_initialize hook."
            )

    @hookimpl(tryfirst=True)
    def initialize_job(self, context: JobContext) -> None:
        """
        This is called during vdk run (job execution) and here we know the job directory
        and can try to infer where the keytab file is.
        """
        kerberos_configuration = KerberosPluginConfiguration(
            context.name, str(context.job_directory), context.core_context.configuration
        )
        self.__attempt_kerberos_authentication(kerberos_configuration)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(KerberosPlugin())
