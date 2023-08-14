# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time
from functools import partial
from unittest import mock

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
from testcontainers.core.waiting_utils import wait_for
from vdk.plugin.postgres import postgres_plugin
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_POSTGRES_DBNAME = "VDK_POSTGRES_DBNAME"
VDK_POSTGRES_USER = "VDK_POSTGRES_USER"
VDK_POSTGRES_PASSWORD = "VDK_POSTGRES_PASSWORD"
VDK_POSTGRES_HOST = "VDK_POSTGRES_HOST"
VDK_POSTGRES_PORT = "VDK_POSTGRES_PORT"


@wait_container_is_ready(Exception)
def wait_for_postgres_to_be_responsive(runner):
    result = runner.invoke(["postgres-query", "--query", "SELECT 1"])
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
        VDK_DB_DEFAULT_TYPE: "POSTGRES",
        VDK_POSTGRES_DBNAME: "postgres",
        VDK_POSTGRES_USER: "postgres",
        VDK_POSTGRES_PASSWORD: "postgres",
        VDK_POSTGRES_HOST: "localhost",
        VDK_POSTGRES_PORT: "5432",
    },
)
def postgres_service(request):
    """Ensure that Postgres service is up and responsive."""
    port = int(os.environ[VDK_POSTGRES_PORT])
    container = (
        DockerContainer("postgres:latest")
        .with_bind_ports(port, port)
        .with_env("POSTGRES_PASSWORD", os.environ[VDK_POSTGRES_PASSWORD])
    )

    try:
        container.start()
        runner = CliEntryBasedTestRunner(postgres_plugin)
        wait_for_postgres_to_be_responsive(runner)
        # wait 2 seconds to make sure the service is up and responsive
        # might be unnecessary but it's out of abundance of caution
        time.sleep(2)
        print(
            f"Postgres service started on port {container.get_exposed_port(port)} and host {container.get_container_host_ip()}"
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to start Postgres service: {e}\n"
            f"Container logs: {container.get_logs()}"
        ) from e

    def stop_container():
        container.stop()
        print("Postgres service stopped")

    request.addfinalizer(stop_container)

    return container
