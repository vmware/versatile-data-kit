# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time
from functools import partial
from unittest import mock

import pytest
from click.testing import Result
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
from testcontainers.core.waiting_utils import wait_for
from vdk.plugin.impala import impala_plugin
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_IMPALA_HOST = "VDK_IMPALA_HOST"
VDK_IMPALA_PORT = "VDK_IMPALA_PORT"


@wait_container_is_ready(Exception)
def wait_for_impala_to_be_responsive(runner):
    result: Result = runner.invoke(["impala-query", "--query", "SELECT 1"])
    if result.exit_code == 0:
        return True
    else:
        raise ConnectionError(
            f"Validation query failed with error {str(result.output)}"
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
def impala_service(request):
    """Ensure that Impala service is up and responsive."""
    port = int(os.environ[VDK_IMPALA_PORT])
    container = DockerContainer("cpcloud86/impala:latest").with_bind_ports(port, port)

    try:
        container.start()
        runner = CliEntryBasedTestRunner(impala_plugin)
        wait_for_impala_to_be_responsive(runner)
        # wait 2 seconds to make sure the service is up and responsive
        # might be unnecessary but it's out of abundance of caution
        time.sleep(2)
        print(
            f"Impala service started on port {container.get_exposed_port(port)} and host {container.get_container_host_ip()}"
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to start Impala service: {e}\n"
            f"Container logs: {container.get_logs()}"
        ) from e

    def stop_container():
        container.stop()
        print("Impala service stopped")

    request.addfinalizer(stop_container)

    return container
