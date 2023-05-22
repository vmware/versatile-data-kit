# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import re
import time
from datetime import date
from datetime import datetime
from unittest import mock

from click.testing import Result
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from taurus_datajob_api import DataJobDeployment
from taurus_datajob_api import DataJobExecution
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.dag import dag_plugin
from vdk.plugin.dag import dag_runner
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from werkzeug import Request
from werkzeug import Response


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class DummyDAGPluginConfiguration:
    def __init__(self):
        self.dags_delayed_jobs_min_delay_seconds_value = 30
        self.dags_delayed_jobs_randomized_added_delay_seconds_value = 600
        self.dags_dag_execution_check_time_period_seconds_value = 10
        self.dags_time_between_status_check_seconds_value = 40
        self.dags_max_concurrent_running_jobs_value = 15

    def dags_delayed_jobs_min_delay_seconds(self):
        return self.dags_delayed_jobs_min_delay_seconds_value

    def dags_delayed_jobs_randomized_added_delay_seconds(self):
        return self.dags_delayed_jobs_randomized_added_delay_seconds_value

    def dags_dag_execution_check_time_period_seconds(self):
        return self.dags_dag_execution_check_time_period_seconds_value

    def dags_time_between_status_check_seconds(self):
        return self.dags_time_between_status_check_seconds_value

    def dags_max_concurrent_running_jobs(self):
        return self.dags_max_concurrent_running_jobs_value


dummy_config = DummyDAGPluginConfiguration()


class TestDAG:
    def _prepare(self, dag_name=None):
        rest_api_url = self.httpserver.url_for("")
        team_name = "team-awesome"
        if self.jobs is None:
            self.jobs = [("job" + str(i), [200], "succeeded", 0) for i in range(1, 5)]

        started_jobs = dict()

        for job_name, request_responses, job_status, *execution_duration in self.jobs:
            request_responses.reverse()
            execution_duration = execution_duration[0] if execution_duration else 0

            def handler(location, statuses, job_name):
                def _handler_fn(r: Request):
                    status = statuses[0] if len(statuses) == 1 else statuses.pop()
                    if status < 300:
                        started_jobs[job_name] = time.time()
                    return Response(status=status, headers=dict(Location=location))

                return _handler_fn

            self.httpserver.expect_request(
                uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/production/executions",
                method="POST",
            ).respond_with_handler(
                handler(
                    f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{job_name}",
                    request_responses,
                    job_name,
                )
            )

            def exec_handler(job_name, job_status, execution_duration):
                def _handler_fn(r: Request):
                    actual_job_status = job_status
                    if time.time() < started_jobs.get(job_name, 0) + execution_duration:
                        actual_job_status = "running"
                    execution: DataJobExecution = DataJobExecution(
                        id=job_name,
                        job_name=job_name,
                        logs_url="http://url",
                        deployment=DataJobDeployment(),
                        start_time="2021-09-24T14:14:03.922Z",
                        status=actual_job_status,
                        message="foo",
                        started_by="manual/" + dag_name,
                    )
                    response_data = json.dumps(
                        execution.to_dict(), indent=4, default=json_serial
                    )
                    return Response(
                        response_data,
                        status=200,
                        headers=None,
                        content_type="application/json",
                    )

                return _handler_fn

            self.httpserver.expect_request(
                uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{job_name}",
                method="GET",
            ).respond_with_handler(
                exec_handler(job_name, job_status, execution_duration)
            )

            class MatchExecutionID:
                def __eq__(self, other):
                    return (
                        re.match(
                            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-\d+$",
                            other.split("/")[-1],
                        )
                        is not None
                    )

            def exec_id_handler(job_name):
                def _handler_fn(r: Request):
                    execution: DataJobExecution = DataJobExecution(
                        id=job_name,
                        job_name=job_name,
                        logs_url="http://url",
                        deployment=DataJobDeployment(),
                        start_time="2021-09-24T14:14:03.922Z",
                        status="succeeded",
                        message="foo",
                        started_by="manual/" + dag_name,
                    )
                    response_data = json.dumps(
                        execution.to_dict(), indent=4, default=json_serial
                    )
                    return Response(
                        response_data,
                        status=200,
                        headers=None,
                        content_type="application/json",
                    )

                return _handler_fn

            self.httpserver.expect_request(
                uri=MatchExecutionID(),
                method="GET",
            ).respond_with_handler(exec_id_handler(job_name))

            def exec_list_handler(job_name):
                def _handler_fn(r: Request):
                    execution: DataJobExecution = DataJobExecution(
                        id=f"{job_name}-latest",
                        job_name=job_name,
                        logs_url="http://url",
                        deployment=DataJobDeployment(),
                        start_time="2021-09-24T14:14:03.922Z",
                        status="succeeded",
                        message="foo",
                        started_by="manual/" + dag_name,
                    )
                    response_data = json.dumps(
                        [execution.to_dict()], indent=4, default=json_serial
                    )
                    return Response(
                        response_data,
                        status=200,
                        headers=None,
                        content_type="application/json",
                    )

                return _handler_fn

            self.httpserver.expect_request(
                uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions",
                method="GET",
            ).respond_with_handler(exec_list_handler(job_name))

        return rest_api_url

    def _set_up(self, jobs=None, additional_env_vars=None, dag_name=None):
        self.httpserver = PluginHTTPServer()
        self.httpserver.start()
        self.jobs = jobs
        self.api_url = self._prepare(dag_name)
        self.env_vars = {"VDK_CONTROL_SERVICE_REST_API_URL": self.api_url}
        if additional_env_vars is not None:
            self.env_vars.update(additional_env_vars)

    def _run_dag(self, dag_name):
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            dag_runner.DAG_CONFIG = dummy_config
            # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
            # and mock large parts of it - e.g passed our own plugins
            result: Result = self.runner.invoke(
                [
                    "run",
                    jobs_path_from_caller_directory(dag_name),
                ]
            )

            return result

    def _assert_dag_fails_with_error(self, result, error):
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            assert isinstance(result.exception, error)
            # no other request should be tried as the DAG fails
            assert len(self.httpserver.log) == 0

    def test_dag(self):
        dag = "dag"
        self._set_up(dag_name=dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            cli_assert_equal(0, result)
            self.httpserver.stop()

    def test_dag_error(self):
        jobs = [
            ("job1", [200], "succeeded"),
            ("job2", [200], "succeeded"),
            ("job3", [200], "platform_error"),
            ("job4", [200], "succeeded"),
        ]
        dag = "dag"
        self._set_up(jobs, dag_name=dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            cli_assert_equal(1, result)
            self.httpserver.stop()

    def test_dag_fail_false(self):
        jobs = [
            ("job1", [200], "succeeded"),
            ("job2", [200], "platform_error"),
            ("job3", [200], "succeeded"),
            ("job4", [200], "succeeded"),
        ]
        dag = "dag"
        self._set_up(jobs, dag_name=dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            cli_assert_equal(0, result)
            self.httpserver.stop()

    def test_dag_conflict(self):
        jobs = [
            ("job1", [409, 200], "succeeded"),
            ("job2", [500, 200], "succeeded"),
            ("job3", [200], "succeeded"),
            ("job4", [200], "succeeded"),
        ]
        dag = "dag"
        env_vars = {
            "VDK_DAGS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS": "0",
            "VDK_DAGS_DELAYED_JOBS_MIN_DELAY_SECONDS": "0",
        }
        self._set_up(jobs, env_vars, dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            cli_assert_equal(0, result)
            self.httpserver.stop()

    def test_dag_cannot_start_job(self):
        jobs = [
            ("job1", [401, 200], "succeeded"),
            ("job2", [200], "succeeded"),
            ("job3", [200], "succeeded"),
            ("job4", [200], "succeeded"),
        ]
        dag = "dag"
        self._set_up(jobs, dag_name=dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            cli_assert_equal(1, result)
            # we should have 3 requests in the log, one to get
            # the execution type of the dag,a list of all
            # executions and one for the failing data job no
            # other request should be tried as the DAG fails
            assert len(self.httpserver.log) == 3
            self.httpserver.stop()

    def test_dag_long_running(self):
        jobs = [
            ("job1", [200], "succeeded", 3),  # execution duration is 3 seconds
            ("job2", [200], "succeeded"),
            ("job3", [200], "succeeded"),
            ("job4", [200], "succeeded"),
        ]
        dag = "dag"
        # we set 5 seconds more than execution duration of 3 set above
        dummy_config.dags_time_between_status_check_seconds_value = 5
        dummy_config.dags_dag_execution_check_time_period_seconds_value = 0

        self._set_up(jobs, dag_name=dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            cli_assert_equal(0, result)
            job1_requests = [
                req
                for req, res in self.httpserver.log
                if req.method == "GET" and req.base_url.endswith("job1")
            ]
            # We have 1 call during start, 1 call at finish and 1 call that returns running and 1 that returns the final
            # status. For total of 4
            # NB: test (verification) that requires that deep implementation details knowledge is
            # not a good idea but we need to verify that we are not hammering the API Server somehow ...
            assert len(job1_requests) == 4

            # let's make sure something else is not generating more requests then expected
            # if implementation is changed the number below would likely change.
            # If the new count is not that big we can edit it here to pass the test,
            # if the new count is too big, we have an issue that need to be investigated.
            assert len(self.httpserver.log) == 22
            self.httpserver.stop()

    def test_dag_concurrent_running_jobs_limit(self):
        jobs = [("job" + str(i), [200], "succeeded", 1) for i in range(1, 8)]
        dag = "dag-exceed-limit"

        dummy_config.dags_max_concurrent_running_jobs_value = 2
        dummy_config.dags_delayed_jobs_min_delay_seconds_value = 1
        dummy_config.dags_delayed_jobs_randomized_added_delay_seconds_value = 1
        dummy_config.dags_time_between_status_check_seconds_value = 1

        env_vars = {
            "VDK_DAGS_MAX_CONCURRENT_RUNNING_JOBS": "2",
            "VDK_DAGS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS": "1",
            "VDK_DAGS_DELAYED_JOBS_MIN_DELAY_SECONDS": "1",
            "VDK_DAGS_TIME_BETWEEN_STATUS_CHECK_SECONDS_VALUE": "1",
        }

        self._set_up(jobs, env_vars, dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            expected_max_running_jobs = int(
                os.getenv("VDK_DAGS_MAX_CONCURRENT_RUNNING_JOBS", "2")
            )
            # keep track of the number of running jobs at any given time
            running_jobs = set()
            for request, response in self.httpserver.log:
                if "executions" in request.path:
                    if request.method == "POST":
                        job_name = request.path.split("/jobs/")[1].split("/")[0]
                        running_jobs.add(job_name)
                        assert (
                            len(running_jobs) <= expected_max_running_jobs
                        )  # assert that max concurrent running jobs is not exceeded
                    if request.method == "GET":
                        execution = json.loads(response.response[0])
                        if isinstance(execution, list):
                            execution = execution[0]
                        if execution["status"] == "succeeded":
                            running_jobs.discard(execution["job_name"])
            cli_assert_equal(0, result)
            # assert that all the jobs finished successfully
            assert len(running_jobs) == 0
            self.httpserver.stop()

    def test_dag_execution_type_propagation(self):
        dag = "dag"
        self._set_up(dag_name=dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            for request, response in self.httpserver.log:
                if "executions" in request.path:
                    if request.method == "GET":
                        execution = json.loads(response.response[0])
                        if isinstance(execution, list):
                            execution = execution[0]
                        assert execution["started_by"] == "manual/" + dag
            cli_assert_equal(0, result)
            self.httpserver.stop()

    def _test_dag_validation(self, dag_name):
        self._set_up()
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag_name)
            cli_assert_equal(1, result)
            self._assert_dag_fails_with_error(result, UserCodeError)
            self.httpserver.stop()

    def test_dag_circular_dependency(self):
        self._test_dag_validation("dag-circular-dep")

    def test_dag_depends_on_itself(self):
        self._test_dag_validation("dag-depends-on-itself")

    def test_dag_duplicate_jobs(self):
        self._test_dag_validation("dag-duplicate-jobs")

    def test_dag_not_allowed_job_key(self):
        self._test_dag_validation("dag-not-allowed-job-key")

    def test_dag_wrong_job_arguments_type(self):
        self._test_dag_validation("dag-wrong-job-arguments-type")

    def test_dag_arguments(self):
        dag = "dag-arguments"
        self._set_up(dag_name=dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            cli_assert_equal(0, result)
            job2_arguments = self._get_job_arguments("job2")
            assert len(job2_arguments) == 2
            assert job2_arguments == {"table_name": "test_table", "counter": 123}
            self.httpserver.stop()

    def test_dag_empty_arguments(self):
        dag = "dag-empty-arguments"
        self._set_up(dag_name=dag)
        with mock.patch.dict(
            os.environ,
            self.env_vars,
        ):
            self.runner = CliEntryBasedTestRunner(dag_plugin)
            result = self._run_dag(dag)
            cli_assert_equal(0, result)
            job2_arguments = self._get_job_arguments("job2")
            assert len(job2_arguments) == 0
            self.httpserver.stop()

    def test_dag_wrong_job_key_type(self):
        self._test_dag_validation("dag-wrong-job-key-type")

    def test_dag_wrong_job_type(self):
        self._test_dag_validation("dag-wrong-job-type")

    def test_dag_wrong_topological_order(self):
        self._test_dag_validation("dag-wrong-topological-order")

    def _get_job_arguments(self, job_name: str):
        job_post_req = [
            req
            for req, res in self.httpserver.log
            if req.method == "POST"
            and req.path.split("/jobs/")[1].split("/")[0] == job_name
        ]
        return job_post_req[0].json["args"]
