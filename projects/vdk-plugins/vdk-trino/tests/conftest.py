# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time
from unittest import mock

import pytest
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.trino import trino_plugin

VDK_TRINO_HOST = "VDK_TRINO_HOST"
VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"


def is_responsive(runner):
    try:
        result = runner.invoke(["trino-query", "--query", "SELECT 1"])
        if result.exit_code == 0:
            return True
    except:
        return False


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "docker-compose.yml"
    )


@pytest.fixture(scope="session")
@mock.patch.dict(
    os.environ,
    {
        VDK_TRINO_HOST: "localhost",
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
    },
)
def trino_service(docker_ip, docker_services):
    """Ensure that Trino service is up and responsive."""
    # os.system("echo Check open ports:")
    # os.system("ss -lntu")
    runner = CliEntryBasedTestRunner(trino_plugin)

    # give the server some time to start before checking if it is ready
    # before adding this sleep there were intermittent fails of the CI/CD with error:
    # requests.exceptions.ConnectionError:
    #   ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
    # More info: https://stackoverflow.com/questions/383738/104-connection-reset-by-peer-socket-error-or-when-does-closing-a-socket-resu
    time.sleep(3)

    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.3, check=lambda: is_responsive(runner)
    )
