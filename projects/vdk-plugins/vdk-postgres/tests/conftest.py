# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time
from unittest import mock

import pytest
from vdk.plugin.postgres import postgres_plugin
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_POSTGRES_DBNAME = "VDK_POSTGRES_DBNAME"
VDK_POSTGRES_USER = "VDK_POSTGRES_USER"
VDK_POSTGRES_PASSWORD = "VDK_POSTGRES_PASSWORD"
VDK_POSTGRES_HOST = "VDK_POSTGRES_HOST"
VDK_POSTGRES_PORT = "VDK_POSTGRES_PORT"


def _is_responsive(runner):
    try:
        result = runner.invoke(["postgres-query", "--query", "SELECT 1"])
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
        VDK_DB_DEFAULT_TYPE: "POSTGRES",
        VDK_POSTGRES_DBNAME: "postgres",
        VDK_POSTGRES_USER: "postgres",
        VDK_POSTGRES_PASSWORD: "postgres",
        VDK_POSTGRES_HOST: "localhost",
        VDK_POSTGRES_PORT: "5432",
    },
)
def postgres_service(docker_ip, docker_services):
    """Ensure that Postgres service is up and responsive."""
    runner = CliEntryBasedTestRunner(postgres_plugin)

    # give the server some time to start before checking if it is ready
    # before adding this sleep there were intermittent fails of the CI/CD with error:
    # requests.exceptions.ConnectionError:
    #   ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
    # More info: https://stackoverflow.com/questions/383738/104-connection-reset-by-peer-socket-error-or-when-does-closing-a-socket-resu
    time.sleep(3)

    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.3, check=lambda: _is_responsive(runner)
    )
