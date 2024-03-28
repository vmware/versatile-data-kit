# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from typing import Dict

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext

VDK_ = "VDK_"


log = logging.getLogger(__name__)


class SecretsConfigPlugin:
    def __normalize_env_key(self, key):
        return key.replace("-", "_").replace(".", "_").upper()

    def _get_env_var(self, key, env: Dict[str, str]):
        normalized_key = self.__normalize_env_key(key)
        normalized_key_with_vdk_prefix = VDK_ + normalized_key
        value = (
            env.get(normalized_key_with_vdk_prefix)
            if normalized_key_with_vdk_prefix in env
            else env.get(normalized_key)
        )
        return value

    @hookimpl(trylast=True)
    def initialize_job(self, context: JobContext):
        upper_cased_env = {k.upper(): v for k, v in os.environ.items()}
        secrets = context.job_input.get_all_secrets()
        for key, value in secrets.items():
            env_var = self._get_env_var(key, upper_cased_env)
            # override only if there is no corresponding environment variable
            if env_var is None:
                log.info(f"Overriding config {key} with secret")
                context.core_context.configuration.override_value(key, value)
