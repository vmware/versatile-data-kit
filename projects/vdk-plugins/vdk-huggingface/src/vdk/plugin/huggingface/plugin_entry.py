# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List
from typing import Optional

import huggingface_hub
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.huggingface.ingest import IngestToHuggingface

HUGGINGFACE_REPO_ID = "huggingface_repo_id"
HUGGINGFACE_TOKEN = "huggingface_token"

log = logging.getLogger(__name__)


class HuggingfacePlugin:
    def __init__(self):
        self._ingester: Optional[IngestToHuggingface] = None

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder):
        config_builder.add(
            key=HUGGINGFACE_TOKEN,
            default_value=None,
            description="HuggingFace API token for authentication. "
            "Get one from https://huggingface.co/settings/tokens",
        )
        config_builder.add(
            key=HUGGINGFACE_REPO_ID,
            default_value="username/test-dataset",
            description="HuggingFace Dataset repository ID.",
        )

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        repo_id = context.core_context.configuration.get_value(HUGGINGFACE_REPO_ID)
        token = context.core_context.configuration.get_value(HUGGINGFACE_TOKEN)

        if token:
            log.debug("huggingface log in", extra={"huggingface_repo_id": repo_id})
            huggingface_hub.login(token)

        self._ingester = IngestToHuggingface(repo_id)

        context.ingester.add_ingester_factory_method(
            "huggingface", lambda: self._ingester
        )

    @hookimpl(trylast=True)
    def finalize_job(self, context: JobContext) -> None:
        if self._ingester:
            self._ingester.commit_all()
        # TODO: on exception , this doesn't fail the job ...


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(
        HuggingfacePlugin(), "HuggingfacePlugin"
    )
