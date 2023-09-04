# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.plugin.ipython.job import load_job
from vdk.plugin.ipython.job import magic_load_job
from vdk.plugin.ipython.sql import vdksql

log = logging.getLogger(__name__)


# see https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.hooks.html for more options


def load_ipython_extension(ipython):
    """
    Function that registers %reload_VDK magic
    IPython will look for this function specifically.
    See https://ipython.readthedocs.io/en/stable/config/extensions/index.html
    """
    ipython.register_magic_function(magic_load_job, magic_name="reload_VDK")
    ipython.register_magic_function(vdksql, magic_kind="cell", magic_name="vdksql")
