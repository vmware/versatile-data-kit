# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
from json import JSONDecodeError
from typing import Any
from typing import List

import werkzeug
from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.httpserver import QueryMatcher
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal import test_utils
from vdk.internal.control.command_groups.job.list import list_command
from vdk.internal.control.command_groups.job.show import show_command

test_utils.disable_vdk_authentication()


def _get_data_job_info():
    data = {
        "job_name": "test-job",
        "description": "Description",
        "config": {
            "contacts": {
                "notified_on_job_failure_user_error": [
                    "starshot_ops@vmware.com",
                    "auserov@vmware.com",
                ],
                "notified_on_job_failure_platform_error": [
                    "starshot_ops@vmware.com",
                    "auserov@vmware.com",
                ],
                "notified_on_job_success": ["auserov@vmware.com"],
                "notified_on_job_deploy": [],
            },
            "schedule": {"schedule_cron": "0 0 13 * 5"},
            "enable_execution_notifications": False,
            "notification_delay_period_minutes": 60,
        },
        "team": "test-team",
    }
    return data


def _get_deployment_info():
    data = [
        {
            "enabled": False,
            "job_version": "11a403ba",
            "mode": "testing",
            "last_deployed_by": "user",
            "last_deployed_date": "2021-02-25T09:16:53.323Z",
        }
    ]
    return data


def _get_executions_info():
    data = [
        {
            "id": "test-vdk-latest-1625735700",
            "job_name": "test-job",
            "status": "platform_error",
            "type": "scheduled",
            "start_time": "2021-07-08T09:15:08+00:00",
            "op_id": "test-vdk-latest-1625735700",
        },
        {
            "id": "test-vdk-latest-1625736000",
            "job_name": "test-job",
            "status": "platform_error",
            "type": "scheduled",
            "start_time": "2021-07-08T09:20:22+00:00",
            "op_id": "test-vdk-latest-1625736000",
            "deployment": {
                "job_version": "09985dbbf9097f92ab4b5891f44f8d2030eb7397",
            },
        },
        {
            "id": "test-vdk-latest-1625736300",
            "job_name": "test-job",
            "status": "platform_error",
            "type": "scheduled",
            "start_time": "2021-07-08T09:25:10+00:00",
            "op_id": "test-vdk-latest-1625736300",
            "deployment": {
                "job_version": "09985dbbf9097f92ab4b5891f44f8d2030eb7397",
            },
        },
    ]
    return data


def test_show(httpserver: PluginHTTPServer):
    rest_api_url = httpserver.url_for("")

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job", method="GET"
    ).respond_with_json(_get_data_job_info())

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments", method="GET"
    ).respond_with_json(_get_deployment_info())

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/executions", method="GET"
    ).respond_with_json(_get_executions_info())

    runner = CliRunner()
    result = runner.invoke(
        show_command,
        ["-o", "json", "-n", "test-job", "-t", "test-team", "-u", rest_api_url],
    )
    test_utils.assert_click_status(result, 0)

    json_output = json.loads(result.output)
    assert json_output is not None
    assert json_output["job_name"] == "test-job"
    assert json_output["deployments"]
    assert len(json_output["executions"]) == 2
