# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.jobs_troubleshoot.troubleshoot_configuration import (
    TROUBLESHOOT_PORT_TO_USE,
)
from vdk.plugin.jobs_troubleshoot.troubleshoot_configuration import (
    TROUBLESHOOT_UTILITIES_TO_USE,
)
from vdk.plugin.jobs_troubleshoot.troubleshoot_utilities.utilities_registry import (
    get_utilities_to_use,
)


def test_get_utilities_to_use():
    config_builder = ConfigurationBuilder()
    config_builder.set_value(key=TROUBLESHOOT_UTILITIES_TO_USE, value="thread-dump")
    config_builder.set_value(key=TROUBLESHOOT_PORT_TO_USE, value=8783)
    configuration = config_builder.build()

    utility = get_utilities_to_use(configuration)

    assert isinstance(utility, List)
    assert len(utility) == 1


def test_get_utilities_to_use__nonexistent_utility():
    config_builder = ConfigurationBuilder()
    config_builder.set_value(
        key=TROUBLESHOOT_UTILITIES_TO_USE, value="non-existent-utility"
    )
    config_builder.set_value(key=TROUBLESHOOT_PORT_TO_USE, value=8783)
    configuration = config_builder.build()

    utility = get_utilities_to_use(configuration)

    assert len(utility) == 0
