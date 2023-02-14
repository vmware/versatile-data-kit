# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from threading import Thread
from unittest import mock

from click.testing import Result
from vdk.plugin.jobs_troubleshoot import jobs_troubleshoot_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path


def job_path(job_name: str):
    return get_test_job_path(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))), job_name
    )


def test_thread_dump():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_TROUBLESHOOT_UTILITIES_TO_USE": "thread-dump",
            "VDK_PORT_TO_USE": "8783",
        },
    ):
        # create table first, as the ingestion fails otherwise
        runner = CliEntryBasedTestRunner(jobs_troubleshoot_plugin)

        result: Result = runner.invoke(["run", job_path("request-thread-dump")])
        cli_assert_equal(0, result)
        assert "Dumping threads stacks" in result.stdout


def test_thread_dump_used_port():
    port = 8783
    server = HTTPServer(("", port), SimpleHTTPRequestHandler)
    thread = Thread(target=server.serve_forever)

    try:
        thread.start()
        with mock.patch.dict(
            os.environ,
            {
                "VDK_TROUBLESHOOT_UTILITIES_TO_USE": "thread-dump",
                "VDK_PORT_TO_USE": f"{port}",
            },
        ):
            # create table first, as the ingestion fails otherwise
            runner = CliEntryBasedTestRunner(jobs_troubleshoot_plugin)

            result: Result = runner.invoke(["run", job_path("request-thread-dump")])
            cli_assert_equal(0, result)
            assert "Dumping threads stacks" in result.stdout
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
