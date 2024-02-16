# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext


class SecretsConfigPlugin:
    @hookimpl(trylast=True)
    def initialize_job(self, context: JobContext):
        secrets = context.job_input.get_all_secrets()
        for key, value in secrets.items():
            context.core_context.configuration.override_value(key, value)
