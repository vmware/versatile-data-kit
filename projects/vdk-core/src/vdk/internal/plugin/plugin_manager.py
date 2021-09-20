# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from pluggy import PluginManager


class VdkPluginManager(PluginManager):
    """
    Abstract away direct access (in terms of imports) to pluggy PluginManager.
    """

    pass
