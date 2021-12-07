# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.control.configuration.vdk_config import VDKConfigFolder

TEAM_OPTION = "team-name"
REST_API_URL_OPTION = "rest-api-url"
AUTHENTICATION_DISABLE = "authentication-disable"

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


def load_default_rest_api_url():
    return VDKConfigFolder().read_configuration(
        section=DEFAULTS_SECTION, option=REST_API_URL_OPTION
    )


def write_default_rest_api_url(default_rest_api_url):
    VDKConfigFolder().write_configuration(
        section=DEFAULTS_SECTION, option=REST_API_URL_OPTION, value=default_rest_api_url
    )


def reset_default_rest_api_url():
    VDKConfigFolder().reset_configuration(
        section=DEFAULTS_SECTION, option=REST_API_URL_OPTION
    )
