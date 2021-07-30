# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.vdk.control.configuration.vdk_config import VDKConfigFolder

TEAM_OPTION = "team-name"

DEFAULTS_SECTION = "defaults"


def load_default_team_name():
    return VDKConfigFolder().read_configuration(
        section=DEFAULTS_SECTION, option=TEAM_OPTION
    )


def write_default_team_name(default_team_name):
    VDKConfigFolder().write_configuration(
        section=DEFAULTS_SECTION, option=TEAM_OPTION, value=default_team_name
    )


def reset_default_team_name():
    VDKConfigFolder().reset_configuration(section=DEFAULTS_SECTION, option=TEAM_OPTION)
