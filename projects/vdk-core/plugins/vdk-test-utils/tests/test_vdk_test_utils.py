# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.vdk.test_utils import util_funcs
from taurus.vdk.test_utils import util_plugins


def test_vdk_test_utils():
    assert util_plugins
    assert util_funcs
