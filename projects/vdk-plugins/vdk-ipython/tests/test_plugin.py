# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import time

import pytest
from IPython.core.error import UsageError
from IPython.testing.globalipapp import start_ipython
from vdk.api.job_input import IJobInput
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk_ipython import JobControl

_log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def session_ip():
    yield start_ipython()


@pytest.fixture(scope="function")
def ip(session_ip):
    session_ip.run_line_magic(magic_name="load_ext", line="vdk_ipython")
    session_ip.run_line_magic(magic_name="reload_VDK", line="")
    yield session_ip
    session_ip.run_line_magic(magic_name="reset", line="-f")


def test_load_vdk_with_no_arguments(ip):
    assert ip.user_global_ns["VDK"] is not None
    assert isinstance(ip.user_global_ns["VDK"], JobControl)


def test_load_vdk_with_valid_argument(ip):
    ip.run_line_magic(magic_name="reload_VDK", line="--name=test")
    assert ip.user_global_ns["VDK"] is not None
    assert isinstance(ip.user_global_ns["VDK"], JobControl)
    assert ip.user_global_ns["VDK"]._name == "test"


def test_load_vdk_with_invalid_argument(ip):
    with pytest.raises(
        UsageError, match=r"unrecognized arguments: --invalid_arg=dummy"
    ):
        ip.run_line_magic(magic_name="reload_VDK", line="--invalid_arg=dummy")


def test_get_initialized_job_input(ip):
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")

    assert ip.user_global_ns["job_input"] is not None
    assert isinstance(ip.user_global_ns["job_input"], IJobInput)


def test_calling_get_initialise_job_input_multiple_times(ip, tmpdir):
    assert ip.user_global_ns["VDK"] is not None
    assert isinstance(ip.user_global_ns["VDK"], JobControl)

    # first call
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")
    result_job_input = ip.get_ipython().getoutput("job_input")

    # test first called object
    assert ip.user_global_ns["job_input"] is not None
    assert isinstance(ip.user_global_ns["job_input"], IJobInput)

    # second call
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")

    # test second called object
    assert ip.user_global_ns["job_input"] is not None
    assert isinstance(ip.user_global_ns["job_input"], IJobInput)

    # check whether first job_input is the same as the second one
    assert result_job_input == ip.get_ipython().getoutput("job_input")


# uses the pytest tmpdir fixture - https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture
async def test_extension_with_ingestion_job(ip, tmpdir):
    # set environmental variables via Jupyter notebook
    job_dir = str(tmpdir) + "vdk-sqlite.db"
    ip.get_ipython().run_cell("%env VDK_INGEST_METHOD_DEFAULT=sqlite")
    ip.get_ipython().run_cell(f"%env VDK_SQLITE_FILE={job_dir}")
    ip.get_ipython().run_cell("%env VDK_DB_DEFAULT_TYPE=SQLITE")

    # get the job_input
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")

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
    time.sleep(1)

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

    # get the job_input
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")

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


def test_finalise(ip):
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")

    # check whether finalize_job is in the output before calling finalize()
    assert (
        "finalize_job"
        not in ip.get_ipython()
        .run_cell("VDK.job._plugin_registry.hook().__dict__")
        .result
    )

    ip.get_ipython().run_cell("VDK.finalize()")

    # check whether finalize_job is in the output after calling finalize()
    assert (
        "finalize_job"
        in ip.get_ipython().run_cell("VDK.job._plugin_registry.hook().__dict__").result
    )


def test_get_initialized_job_input_multiple_times(ip):
    ip.run_line_magic(magic_name="reload_VDK", line="")

    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")
    first_result = ip.get_ipython().run_cell("job_input").result
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")

    assert first_result == ip.get_ipython().run_cell("job_input").result


def test_get_initialized_job_input_after_finalize(ip):
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")
    ip.get_ipython().run_cell("VDK.finalize()")
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")
    ip.get_ipython().run_cell("VDK.finalize()")
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")

    assert ip.user_global_ns["job_input"] is not None
    assert isinstance(ip.user_global_ns["job_input"], IJobInput)


def test_call_finalize_multiple_times(ip):
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")
    ip.get_ipython().run_cell("VDK.finalize()")
    ip.get_ipython().run_cell("VDK.finalize()")
    # verifying that calling finalize multiple times won't produce any errors (the method will not fail)


def test_call_finalize_before_get_initialized_job_input(ip):
    ip.get_ipython().run_cell("VDK.finalize()")
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")
    ip.get_ipython().run_cell("VDK.finalize()")
    assert (
        "finalize_job"
        in ip.get_ipython().run_cell("VDK.job._plugin_registry.hook().__dict__").result
    )
    # verifying that calling finalize before get_initialized_job_input won't produce errors(the method will not fail)


def test_calling_get_initialise_job_input_multiple_times_after_finalize(ip, tmpdir):
    # first call
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")
    result_job_input = ip.get_ipython().run_cell("job_input").result
    ip.get_ipython().run_cell("VDK.finalize()")

    # second call
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")

    # check whether first job_input is the same as the second one
    assert result_job_input != ip.get_ipython().run_cell("job_input").result


def test_automatic_finalize_after_kernel_shutdown(ip):
    class FinalizeTrackingPlugin:
        # Due to problems with testing atexit functions, this should be tested manually
        # Logs will be introduced, and to see the result of the test we should check logs
        @hookimpl
        def finalize_job(self, context: JobContext) -> None:
            # _log.info("\n\nfinalize_job is called!\n\n")
            print("\n\nfinalize_job is called!\n\n")

    plugin = FinalizeTrackingPlugin()
    ip.get_ipython().push(variables={"plugin": plugin})
    ip.run_line_magic(magic_name="reload_VDK", line="")
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")
