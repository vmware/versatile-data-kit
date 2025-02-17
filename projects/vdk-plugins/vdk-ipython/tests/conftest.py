# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

import pytest
from IPython.testing.globalipapp import start_ipython


@pytest.fixture(scope="session")
def session_ip():
    yield start_ipython()


@pytest.fixture(scope="function")
def ip(session_ip):
    session_ip.run_line_magic(magic_name="load_ext", line="vdk.plugin.ipython")
    session_ip.run_line_magic(magic_name="reload_VDK", line="")
    yield session_ip
    session_ip.run_line_magic(magic_name="reset", line="-f")


@pytest.fixture(scope="function")
def sqlite_ip(ip, tmp_path):
    job_dir = f"{tmp_path}/vdk-sqlite.db"
    ip.get_ipython().run_cell("%env VDK_INGEST_METHOD_DEFAULT=sqlite")
    ip.get_ipython().run_cell(f"%env VDK_SQLITE_FILE={job_dir}")
    ip.get_ipython().run_cell(f"%env VDK_INGEST_TARGET_DEFAULT={job_dir}")
    ip.get_ipython().run_cell("%env VDK_DB_DEFAULT_TYPE=SQLITE")
    ip.get_ipython().run_cell("%env INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND=true")
    yield ip
