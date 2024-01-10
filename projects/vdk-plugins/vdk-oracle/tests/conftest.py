# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time
from unittest import mock

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

ORACLE_IMAGE = "container-registry.oracle.com/database/free:latest"

DB_DEFAULT_TYPE = "DB_DEFAULT_TYPE"
ORACLE_USER = "ORACLE_USER"
ORACLE_PASSWORD = "ORACLE_PASSWORD"
ORACLE_CONNECTION_STRING = "ORACLE_CONNECTION_STRING"
ORACLE_HOST = "ORACLE_HOST"
ORACLE_PORT = "ORACLE_PORT"
ORACLE_SID = "ORACLE_SID"
VDK_LOG_EXECUTION_RESULT = "VDK_LOG_EXECUTION_RESULT"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"


@pytest.fixture(scope="session")
@mock.patch.dict(
    os.environ,
    {
        DB_DEFAULT_TYPE: "oracle",
        ORACLE_USER: "SYSTEM",
        ORACLE_PASSWORD: "Gr0mh3llscr3am",
        ORACLE_HOST: "localhost",
        ORACLE_PORT: "1521",
        ORACLE_SID: "FREE",
        ORACLE_CONNECTION_STRING: "localhost:1521/FREE",
        VDK_LOG_EXECUTION_RESULT: "True",
        VDK_INGEST_METHOD_DEFAULT: "ORACLE",
    },
)
def oracle_db(request):
    port = 1521
    password = os.environ[ORACLE_PASSWORD]
    container = (
        DockerContainer(ORACLE_IMAGE)
        .with_bind_ports(port, port)
        .with_env("ORACLE_PWD", password)
        .with_env("ORACLE_CHARACTERSET", "UTF8")
    )
    try:
        container.start()
        wait_for_logs(
            container,
            "DATABASE IS READY TO USE",
            timeout=120,
        )
        time.sleep(2)
        print(
            f"Oracle db started on port {container.get_exposed_port(port)} and host {container.get_container_host_ip()}"
        )
    except Exception as e:
        print(f"Failed to start Oracle DB: {e}")
        print(f"Container logs: {container.get_logs()}")
        raise e

    def stop_container():
        container.stop()
        print("Oracle DB stopped")

    request.addfinalizer(stop_container)

    return container
