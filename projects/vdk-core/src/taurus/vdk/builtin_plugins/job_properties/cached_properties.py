# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.api.job_input import IProperties


class CachedPropertiesWrapper(IProperties):
    """
    Wraps any IProperties so that get_* calls are cached until set_* is called
    Needed mainly because .sql file execution performs SQL argument substitution. In the general case this means
    invoking HDFS read command, however properties are rarely updated, so a cache reduces HDFS access, thus reducing
    overall job execution time.
    """

    def __init__(self, properties_impl: IProperties):
        self.provider = properties_impl
        self.cached_dict = (
            None  # when None then cache needs to be refreshed on next get_*()
        )

    def get_property(self, name, default_value=None):
        res = self._get_cached_dict().get(name, default_value)
        return res

    def get_all_properties(self):
        return self._get_cached_dict()

    def set_all_properties(self, properties):
        self.provider.set_all_properties(properties)
        self.cached_dict = None

    def _get_cached_dict(self):
        if self.cached_dict is None:
            self.cached_dict = self.provider.get_all_properties()
        return self.cached_dict
