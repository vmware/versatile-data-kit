# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.job_secrets import secrets_config
from vdk.internal.builtin_plugins.job_secrets.inmemsecrets import (
    InMemSecretsServiceClient,
)
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder


class SecretsApiPlugin:
    """
    Define the basic configuration needed for Secrets API.
    """

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        secrets_config.add_definitions(config_builder)

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.secrets.set_secrets_factory_method("memory", InMemSecretsServiceClient)
