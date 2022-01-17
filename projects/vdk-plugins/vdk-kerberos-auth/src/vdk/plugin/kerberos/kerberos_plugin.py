# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.kerberos.authenticator_factory import KerberosAuthenticatorFactory
from vdk.plugin.kerberos.kerberos_configuration import add_definitions
from vdk.plugin.kerberos.kerberos_configuration import KerberosPluginConfiguration

log = logging.getLogger(__name__)


class KerberosPlugin:
    def __init__(self):
        self.__authenticator = None

    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder)

    @hookimpl(tryfirst=True)
    def initialize_job(self, context: JobContext) -> None:
        kerberos_configuration = KerberosPluginConfiguration(
            context.name, str(context.job_directory), context.core_context.configuration
        )
        authenticator_factory = KerberosAuthenticatorFactory(kerberos_configuration)

        try:
            self.__authenticator = authenticator_factory.create_authenticator(
                kerberos_configuration.authentication_type()
            )
        except Exception:
            log.error(
                "Kerberos authenticator cannot be created. You can provide configuration that specifies "
                "keytab info using the following environment variables: VDK_KEYTAB_FOLDER, or "
                "VDK_KEYTAB_FILENAME and VDK_KEYTAB_PRINCIPAL"
            )
            raise

        if self.__authenticator:
            self.__authenticator.authenticate()


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(KerberosPlugin())
