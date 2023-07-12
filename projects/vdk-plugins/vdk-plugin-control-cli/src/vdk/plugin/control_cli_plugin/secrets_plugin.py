# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.control_cli_plugin.control_service_configuration import (
    ControlServiceConfiguration,
)
from vdk.plugin.control_cli_plugin.control_service_secrets_client import (
    ControlServiceSecretsServiceClient,
)

log = logging.getLogger(__name__)


@hookimpl
def initialize_job(context: JobContext) -> None:
    conf = ControlServiceConfiguration(context.core_context.configuration)
    url = conf.control_service_rest_api_url()
    if url:
        log.info("Initialize Control Service based Secrets client implementation.")
        context.secrets.set_secrets_factory_method(
            "default", lambda: ControlServiceSecretsServiceClient(url)
        )
        context.secrets.set_secrets_factory_method(
            "control-service", lambda: ControlServiceSecretsServiceClient(url)
        )
    else:
        log.info(
            "Control Service REST API URL is not configured. "
            "Will not initialize Control Service based Secrets client implementation."
        )
