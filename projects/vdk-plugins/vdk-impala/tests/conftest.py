# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time
from unittest import mock

import pytest
from vdk.plugin.impala import impala_plugin
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_IMPALA_HOST = "VDK_IMPALA_HOST"
VDK_IMPALA_PORT = "VDK_IMPALA_PORT"


def _is_responsive(runner):
    try:
        result = runner.invoke(["impala-query", "--query", "SELECT 1"])
        if result.exit_code == 0:
            return True
    except:
        return False


# TODO:
# We are using pretty old version of Impala for those tests.
# We should consider switching to a newer one
# Impala seem to maintain docker images :
# https://github.com/apache/impala/blob/master/docker/README.md#docker-quickstart-with-docker-compose
@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "docker-compose.yml"
    )


@pytest.fixture(scope="session")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "IMPALA",
        VDK_IMPALA_HOST: "localhost",
        VDK_IMPALA_PORT: "21050",
    },
)
def impala_service(docker_ip, docker_services):
    """Ensure that Impala service is up and responsive."""
    runner = CliEntryBasedTestRunner(impala_plugin)

    # give the server some time to start before checking if it is ready
    # before adding this sleep there were intermittent fails of the CI/CD with error:
    # requests.exceptions.ConnectionError:
    #   ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
    # More info: https://stackoverflow.com/questions/383738/104-connection-reset-by-peer-socket-error-or-when-does-closing-a-socket-resu
    time.sleep(3)

    docker_services.wait_until_responsive(
        timeout=240.0, pause=1, check=lambda: _is_responsive(runner)
    )
    time.sleep(10)
