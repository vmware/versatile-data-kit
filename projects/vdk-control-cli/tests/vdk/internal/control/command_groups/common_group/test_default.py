# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time

from click.testing import CliRunner
from vdk.internal.control.command_groups.common_group.default import (
    reset_default_command,
)
from vdk.internal.control.command_groups.common_group.default import set_default_command
from vdk.internal.control.configuration.vdk_config import VDKConfigFolder

EXPECTED_CONFIG_PATH = os.path.join(
    VDKConfigFolder().vdk_config_folder, VDKConfigFolder.CONFIGURATION_FILE
)


def test_set_default_flow():
    # Setup
    test_team_name = "test-set-team-" + str(time.time())
    team_name_config_content = f"team-name = {test_team_name}"

    # Run
    runner = CliRunner()
    result = runner.invoke(set_default_command, ["--team", test_team_name])

    # Assert
    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}"
    with open(EXPECTED_CONFIG_PATH) as my_file:
        actual_data = my_file.read()
        assert actual_data
        assert team_name_config_content in actual_data

    # Run
    result = runner.invoke(reset_default_command, ["--team"])

    # Assert
    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}"
    with open(EXPECTED_CONFIG_PATH) as my_file:
        actual_data = my_file.read()
        assert team_name_config_content not in actual_data
