# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import pytest

pytest_plugins = ("jupyter_server.pytest_plugin",)


@pytest.fixture
def jp_server_config(jp_server_config):
    return {"ServerApp": {"jpserver_extensions": {"vdk_jupyterlab_extension": True}}}
