# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock
from unittest.mock import patch

from taurus_datajob_api import DataJobDeployment
from taurus_datajob_api import DataJobExecution
from urllib3.exceptions import ReadTimeoutError
from vdk.plugin.meta_jobs.cached_data_job_executor import TrackingDataJobExecutor
from vdk.plugin.meta_jobs.remote_data_job_executor import RemoteDataJobExecutor


def test_get_latest_available_execution_id():
    test_job_id = "awesome-test_job"
    test_execution: DataJobExecution = DataJobExecution(
        id=test_job_id,
        job_name=test_job_id,
        logs_url="http://url",
        deployment=DataJobDeployment(),
        start_time="2021-09-24T14:14:03.922Z",
        status="succeeded",
        message="foo",
    )

    test_executor = MagicMock(spec=RemoteDataJobExecutor)
    test_executor.job_executions_list.side_effect = [[test_execution]]

    tracking_executor = TrackingDataJobExecutor(test_executor)
    assert test_job_id == tracking_executor.get_latest_available_execution_id(
        test_job_id, "awesome-test-team"
    )


def test_get_latest_available_execution_id_return_none():
    test_job_id = "awesome-test-job"

    test_executor = MagicMock(spec=RemoteDataJobExecutor)
    test_executor.job_executions_list.side_effect = [[]]

    tracking_executor = TrackingDataJobExecutor(test_executor)
    assert not tracking_executor.get_latest_available_execution_id(
        test_job_id, "awesome-test-team"
    )


@patch("vdk.plugin.meta_jobs.cached_data_job_executor.SLEEP_TIME", return_value=1)
def test_start_new_job_execution_timeout_error(patched_timeout):
    test_job_id = "awesome-test-job"
    test_timeout_exception = ReadTimeoutError(
        message="Read timed out.", url="http://url", pool=MagicMock()
    )

    test_executor = MagicMock(spec=RemoteDataJobExecutor)
    test_executor.start_job.side_effect = [test_timeout_exception, "awesome-test-job"]
    test_executor.job_executions_list.side_effect = [[], []]

    tracking_executor = TrackingDataJobExecutor(test_executor)
    assert test_job_id == tracking_executor.start_new_job_execution(
        job_name=test_job_id, team_name="awesome-team"
    )
    assert len(test_executor.method_calls) == 4
