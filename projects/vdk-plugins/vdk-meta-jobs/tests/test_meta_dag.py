# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import time
from unittest.mock import call
from unittest.mock import MagicMock

from vdk.plugin.meta_jobs.cached_data_job_executor import TrackingDataJobExecutor
from vdk.plugin.meta_jobs.meta_dag import MetaJobsDag

# We overall eschew unit tests in favor of functional tests in test_meta_job
# Still some functionalities are more easily tested in unit tests so we add here some.


def test_execute_dag_happy_case():
    job1 = dict(job_name="job1", depends_on=[])
    job2 = dict(job_name="job2", depends_on=["job1"])
    job3 = dict(job_name="job3", depends_on=["job1"])
    job4 = dict(job_name="job4", depends_on=["job2", "job3"])
    jobs = [job1, job2, job3, job4]

    dag = MetaJobsDag("team")
    dag.build_dag(jobs)
    dag._job_executor = MagicMock(spec=TrackingDataJobExecutor)
    dag._job_executor.get_finished_job_names.side_effect = [
        ["job1"],
        ["job2", "job3"],
        ["job4"],
    ]

    dag.execute_dag()

    assert [
        call("job1"),
        call("job2"),
        call("job3"),
        call("job4"),
    ] == dag._job_executor.start_job.call_args_list


def test_execute_dag_busyloop():
    job1 = dict(job_name="job1", depends_on=[])
    job2 = dict(job_name="job2", depends_on=["job1"])
    job3 = dict(job_name="job3", depends_on=["job1"])
    jobs = [job1, job2, job3]

    dag = MetaJobsDag("team")
    dag.build_dag(jobs)
    dag._job_executor = MagicMock(spec=TrackingDataJobExecutor)
    dag._dag_execution_check_time_period_seconds = 3

    calls = [0]
    start_time = [0]

    def mock_get_finished_job_names(*args, **kwargs):
        calls[0] += 1
        if calls[0] == 1:
            start_time[0] = time.time()
            return ["job1"]
        elif time.time() - start_time[0] > 2:
            return ["job2", "job3"]
        else:
            return []

    dag._job_executor.get_finished_job_names.side_effect = mock_get_finished_job_names

    dag.execute_dag()

    # check for busyloop (this would have been called hundreds of times if there is busyloop bug)
    assert calls[0] <= 4
