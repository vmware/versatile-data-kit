# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time
from unittest import mock

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

TRINO_IMAGE = "trinodb/trino:latest"

VDK_TRINO_HOST = "VDK_TRINO_HOST"
VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"


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
def trino_service(request):
    """Ensure that Trino service is up and responsive."""
    # os.system("echo Check open ports:")
    # os.system("ss -lntu")
    port = int(os.environ[VDK_TRINO_PORT])
    container = DockerContainer(TRINO_IMAGE).with_bind_ports(port, port)
    try:
        container.start()
        # following instructions in https://hub.docker.com/r/trinodb/trino
        # Wait for the following message log line:
        wait_for_logs(container, "SERVER STARTED", timeout=120)
        # wait 2 seconds to make sure the service is up and responsive
        # might be unnecessary but it's out of abundance of caution
        time.sleep(2)
        print(
            f"Trino service started on port {container.get_exposed_port(port)} and host {container.get_container_host_ip()}"
        )
    except Exception as e:
        print(f"Failed to start Trino service: {e}")
        print(f"Container logs: {container.get_logs()}")
        raise e

    def stop_container():
        container.stop()
        print("Trino service stopped")

    request.addfinalizer(stop_container)

    return container
