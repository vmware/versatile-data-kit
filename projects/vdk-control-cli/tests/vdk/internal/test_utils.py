# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import traceback
from inspect import getabsfile
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join

from click.testing import Result
from resources.unused import UNUSED
from vdk.internal.control.rest_lib.factory import ApiClientFactory


def find_test_resource(resource_relative_path, throw_if_not_found=True):
    """
    param: resource_relative_path: Path to the resource file relative to test-resources/ folder, e.g. 'hello_world_view/bar.sql'
    """
    folder_test_resources = dirname(getabsfile(UNUSED))
    if not exists(folder_test_resources):
        raise Exception(
            "Bug! Folder test-resources does not exist at {}".format(
                folder_test_resources
            )
        )
    res = join(folder_test_resources, resource_relative_path)
    res = abspath(res)
    if throw_if_not_found:
        if not exists(res):
            raise FileNotFoundError("File/folder does not exist: ", res)
    return res


def assert_click_status(result: Result, expected_exit_code):
    assert result.exit_code == expected_exit_code, (
        f"result exit code is not {expected_exit_code},"
        f" result output: {result.output}"
        f"Exception:\n {''.join(traceback.format_exception(*result.exc_info))} "
    )


def allow_oauthlib_insecure_transport():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"


def disable_vdk_authentication():
    os.environ["VDK_AUTHENTICATION_DISABLE"] = "true"


def get_json_response_mock():
    json_response_mock = {
        "id_token": "",
        "token_type": "bearer",
        "expires_in": 1799,
        "scope": "csp:support_user",
        "access_token": "axczfe12casASDCz",
        "refresh_token": "refresh",
    }
    return json_response_mock
