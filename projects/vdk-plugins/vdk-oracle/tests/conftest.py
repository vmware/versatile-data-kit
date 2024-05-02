# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import time
from unittest import mock

import pytest
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.oracle import OracleDbContainer

# from testcontainers.core.container import DockerContainer

ORACLE_IMAGE = "container-registry.oracle.com/database/free:latest"

DB_DEFAULT_TYPE = "DB_DEFAULT_TYPE"
ORACLE_USER = "ORACLE_USER"
ORACLE_PASSWORD = "ORACLE_PASSWORD"
ORACLE_CONNECTION_STRING = "ORACLE_CONNECTION_STRING"
VDK_LOG_EXECUTION_RESULT = "VDK_LOG_EXECUTION_RESULT"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"


@pytest.fixture(scope="session")
@mock.patch.dict(
    os.environ,
    {
        # DB_DEFAULT_TYPE: "oracle",
        # ORACLE_USER: "system",
        # ORACLE_PASSWORD: "oracle",
        # ORACLE_CONNECTION_STRING: "oracle://system:oracle@localhost:1521/xe",
        VDK_LOG_EXECUTION_RESULT: "True",
        VDK_INGEST_METHOD_DEFAULT: "ORACLE",
    },
)
def oracle_db(request):
    port = 1521
    # password = os.environ[ORACLE_PASSWORD]
    first_container = (
        OracleDbContainer()
        .with_bind_ports(port, port)
        .with_env("ORACLE_CHARACTERSET", "UTF8")
        .with_env("ORACLE_PASSWORD", "oracle1")
    )
    # first_container = (
    #     DockerContainer(ORACLE_IMAGE)
    #     .with_bind_ports(port, port)
    #     .with_env("ORACLE_PWD", password)
    #     .with_env("ORACLE_CHARACTERSET", "UTF8")
    # )
    # second_container = (
    #     DockerContainer(ORACLE_IMAGE)
    #     .with_bind_ports(port, 1523)
    #     .with_env("ORACLE_PWD", password)
    #     .with_env("ORACLE_CHARACTERSET", "UTF8")
    # )

    def stop_container():
        first_container.stop()
        print("First Oracle DB stopped")

    #    second_container.stop()
    #    print("Second Oracle DB stopped")

    request.addfinalizer(stop_container)
    first_container.start()
    # try:
    #     first_container.start()
    #     wait_for_logs(
    #         first_container,
    #         "DATABASE IS READY TO USE",
    #         timeout=120,
    #     )
    #     time.sleep(2)
    #     print(
    #         f"Oracle db started on port {first_container.get_exposed_port(port)} and host {first_container.get_container_host_ip()}"
    #     )
    # except Exception as e:
    #     print(f"Failed to start Oracle DB: {e}")
    #     print(f"Container logs: {first_container.get_logs()}")
    #     raise e

    # try:
    #     second_container.start()
    #     wait_for_logs(
    #         second_container,
    #         "DATABASE IS READY TO USE",
    #         timeout=120,
    #     )
    #     time.sleep(2)
    #     print(
    #         f"Oracle db started on port {second_container.get_exposed_port(port)} and host {second_container.get_container_host_ip()}"
    #     )
    # except Exception as e:
    #     print(f"Failed to start Oracle DB: {e}")
    #     print(f"Container logs: {second_container.get_logs()}")
    #     raise e

    # return container
