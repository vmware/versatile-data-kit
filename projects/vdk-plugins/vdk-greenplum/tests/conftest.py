# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import time
from functools import partial
from unittest import mock

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for
from vdk.plugin.greenplum import greenplum_plugin
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_GREENPLUM_DBNAME = "VDK_GREENPLUM_DBNAME"
VDK_GREENPLUM_USER = "VDK_GREENPLUM_USER"
VDK_GREENPLUM_PASSWORD = "VDK_GREENPLUM_PASSWORD"
VDK_GREENPLUM_HOST = "VDK_GREENPLUM_HOST"
VDK_GREENPLUM_PORT = "VDK_GREENPLUM_PORT"

log = logging.getLogger(__name__)


def _is_responsive(runner):
    try:
        result = runner.invoke(["greenplum-query", "--query", "SELECT 1"])
        if result.exit_code == 0:
            return True
    except Exception as e:
        raise ConnectionError(str(e)) from e


@pytest.fixture(scope="session")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "GREENPLUM",
        VDK_GREENPLUM_DBNAME: "postgres",
        VDK_GREENPLUM_USER: "gpadmin",
        VDK_GREENPLUM_PASSWORD: "pivotal",
        VDK_GREENPLUM_HOST: "localhost",
        VDK_GREENPLUM_PORT: "5432",
    },
)
def greenplum_service(request):
    """Ensure that Greenplum service is up and responsive."""
    # os.system("echo Check open ports:")
    # os.system("ss -lntu")
    port = int(os.environ[VDK_GREENPLUM_PORT])
    container = (
        DockerContainer("datagrip/greenplum:6.8")
        .with_bind_ports(port, port)
        .with_env("GREENPLUM_USER", os.environ[VDK_GREENPLUM_PORT])
        .with_env("GREENPLUM_PASSWORD", os.environ[VDK_GREENPLUM_PASSWORD])
    )

    try:
        container.start()
        runner = CliEntryBasedTestRunner(greenplum_plugin)
        wait_for(partial(_is_responsive, runner))
        # wait 2 seconds to make sure the service is up and responsive
        # might be unnecessary but it's out of abundance of caution
        time.sleep(2)
        log.info(
            f"Greenplum service started on port {container.get_exposed_port(port)} and host {container.get_container_host_ip()}"
        )
    except Exception as e:
        log.info(f"Failed to start Greenplum service: {e}")
        log.info(f"Container logs: {container.get_logs()}")
        raise e

    def stop_container():
        container.stop()
        log.info("Greenplum service stopped")

    request.addfinalizer(stop_container)

    return container
