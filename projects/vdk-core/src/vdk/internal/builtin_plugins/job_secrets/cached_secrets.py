# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import ISecrets


class CachedSecretsWrapper(ISecrets):
    """
    Wraps any ISecrets so that get_* calls are cached until set_* is called
    Since secrets are rarely updated, it's better to have them cached.
    """

    def __init__(self, secrets_impl: ISecrets):
        self.provider = secrets_impl
        self.cached_dict = (
            None  # when None then cache needs to be refreshed on next get_*()
        )

    def get_secret(self, name, default_value=None):
        res = self._get_cached_dict().get(name, default_value)
        return res

    def get_all_secrets(self):
        return self._get_cached_dict()

    def set_all_secrets(self, secrets):
        self.provider.set_all_secrets(secrets)
        self.cached_dict = None

    def _get_cached_dict(self):
        if self.cached_dict is None:
            self.cached_dict = self.provider.get_all_secrets()
        return self.cached_dict
