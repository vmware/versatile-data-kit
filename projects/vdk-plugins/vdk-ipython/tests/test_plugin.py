# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import asyncio
import logging

import pytest
from IPython.core.error import UsageError
from IPython.testing.globalipapp import start_ipython
from vdk.api.job_input import IJobInput
from vdk_ipython import JobControl


@pytest.fixture(scope="session")
def session_ip():
    yield start_ipython()


@pytest.fixture(scope="function")
def ip(session_ip):
    session_ip.run_line_magic(magic_name="load_ext", line="vdk_ipython")
    yield session_ip
    session_ip.run_line_magic(magic_name="reset", line="-f")


def test_load_data_job_with_no_arguments(ip):
    ip.run_line_magic(magic_name="reload_data_job", line="")
    assert ip.user_global_ns["data_job"] is not None
    assert isinstance(ip.user_global_ns["data_job"], JobControl)


def test_load_data_job_with_valid_argument(ip):
    ip.run_line_magic(magic_name="reload_data_job", line="--name=test")
    assert ip.user_global_ns["data_job"] is not None
    assert isinstance(ip.user_global_ns["data_job"], JobControl)
    assert ip.user_global_ns["data_job"].job._name == "test"


def test_load_data_job_with_invalid_argument(ip):
    with pytest.raises(
        UsageError, match=r"unrecognized arguments: --invalid_arg=dummy"
    ):
        ip.run_line_magic(magic_name="reload_data_job", line="--invalid_arg=dummy")


def test_get_initialized_job_input(ip):
    ip.run_line_magic(magic_name="reload_data_job", line="")
    assert ip.user_global_ns["data_job"] is not None
    assert isinstance(ip.user_global_ns["data_job"], JobControl)
    ip.get_ipython().run_cell("job_input = data_job.get_initialized_job_input()")
    assert ip.user_global_ns["job_input"] is not None
    assert isinstance(ip.user_global_ns["job_input"], IJobInput)


# uses the pytest tmpdir fixture - https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture
async def test_extension_with_ingestion_job(ip, tmpdir):
    # set environmental variables via Jupyter notebook
    job_dir = str(tmpdir) + "vdk-sqlite.db"
    ip.get_ipython().run_cell("%env VDK_INGEST_METHOD_DEFAULT=sqlite")
    ip.get_ipython().run_cell(f"%env VDK_SQLITE_FILE={job_dir}")
    ip.get_ipython().run_cell("%env VDK_DB_DEFAULT_TYPE=SQLITE")

    ip.run_line_magic(magic_name="reload_data_job", line="")

    # get the job_input
    ip.get_ipython().run_cell("job_input = data_job.get_initialized_job_input()")

    # execute SQL using job_input
    ip.get_ipython().run_cell(
        'job_input.execute_query("DROP TABLE IF EXISTS rest_target_table;")'
    )
    ip.get_ipython().run_cell(
        'job_input.execute_query("CREATE TABLE rest_target_table (userId, id, title, completed);")'
    )

    # check whether the table was created
    # the output should look like this:
    #  'userId    id    title    completed',
    #  '--------  ----  -------  -----------'
    assert "userId    id    title    completed" in (
        ip.get_ipython().getoutput(
            "! " "vdk " "sqlite-query -q 'SELECT * FROM rest_target_table'"
        )
    )
    assert "--------  ----  -------  -----------" in (
        ip.get_ipython().getoutput(
            "! " "vdk " "sqlite-query -q 'SELECT * FROM rest_target_table'"
        )
    )

    # get the data that is going to be ingested
    ip.get_ipython().run_cell("import requests")
    ip.get_ipython().run_cell(
        'response = requests.get("https://jsonplaceholder.typicode.com/todos/1")'
    )
    ip.get_ipython().run_cell("payload = response.json()")

    # send data for ingestion
    ip.get_ipython().run_cell(
        'job_input.send_object_for_ingestion(payload=payload,destination_table="rest_target_table")'
    )

    # wait until the table is populated
    await asyncio.sleep(1)

    # check whether output contains the table
    # '  userId    id  title                 completed',
    # '--------  ----  ------------------  -----------',
    # '       1     1  delectus aut autem            0'

    assert "  userId    id  title                 completed" in (
        ip.get_ipython().getoutput(
            "! " "vdk " "sqlite-query -q 'SELECT * FROM rest_target_table'"
        )
    )
    assert "       1     1  delectus aut autem            0" in (
        ip.get_ipython().getoutput(
            "! " "vdk " "sqlite-query -q 'SELECT * FROM rest_target_table'"
        )
    )


def test_extension_with_pure_sql_job(ip, tmpdir):
    # set environmental variables via Jupyter notebook
    job_dir = str(tmpdir) + "vdk-sqlite.db"
    ip.get_ipython().run_cell("%env VDK_INGEST_METHOD_DEFAULT=sqlite")
    ip.get_ipython().run_cell(f"%env VDK_SQLITE_FILE={job_dir}")
    ip.get_ipython().run_cell("%env VDK_DB_DEFAULT_TYPE=SQLITE")

    ip.run_line_magic(magic_name="reload_data_job", line="")

    # get the job_input
    ip.get_ipython().run_cell("job_input = data_job.get_initialized_job_input()")

    # execute SQL using job_input
    ip.get_ipython().run_cell(
        'job_input.execute_query("CREATE TABLE stocks (date text, symbol text, price real)")'
    )
    ip.get_ipython().run_cell(
        "job_input.execute_query(\"INSERT INTO stocks VALUES ('2020-01-01', 'GOOG', 123.0), ('2021-01-01', 'GOOG', "
        '123.0)")'
    )

    # check whether output contains the table:
    # date        symbol      price
    # ----------  --------  -------
    # 2020-01-01  GOOG          123
    # 2020-01-01  GOOG          123
    assert "date        symbol      price" in (
        ip.get_ipython().getoutput("! " "vdk " "sqlite-query -q 'SELECT * FROM stocks'")
    )
    assert "2020-01-01  GOOG          123" in (
        ip.get_ipython().getoutput("! " "vdk " "sqlite-query -q 'SELECT * FROM stocks'")
    )
    assert "2021-01-01  GOOG          123" in (
        ip.get_ipython().getoutput("! " "vdk " "sqlite-query -q 'SELECT * FROM stocks'")
    )
