# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import patch

from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.job_controller import JobController


@patch.object(JobController, "_execute")
def test_check_job_execution_finished(patched_method):
    test_config = Config()
    test_config.control_api_url = None
    test_config.vdkcli_oauth2_uri = None

    patched_method.return_value = (
        '[{"status": "finished", "end_time": ' '"2022-03-01"}]'
    )

    test_controller = JobController(test_config)
    test_controller.config.RUN_TEST_TIMEOUT_SECONDS = 10

    res = test_controller.check_job_execution_finished()
    assert res == "finished"


@patch.object(JobController, "_execute")
def test_check_job_execution_finished_no_exceptions_for_value_errors(patched_method):
    test_config = Config()
    test_config.control_api_url = None
    test_config.vdkcli_oauth2_uri = None

    patched_method.return_value = '[{"status": "finished", "end_time": "None"}]'

    test_controller = JobController(test_config)
    test_controller.config.RUN_TEST_TIMEOUT_SECONDS = 10

    res = test_controller.check_job_execution_finished()
    assert res == "finished"

    # non-populated end_time
    patched_method.return_value = '[{"status": "finished", "end_time": null}]'
    res = test_controller.check_job_execution_finished()
    assert res == "finished"

    patched_method.return_value = '[{"status": "finished", "end_time": ' "12345}]"

    res = test_controller.check_job_execution_finished()
    assert res == "finished"
