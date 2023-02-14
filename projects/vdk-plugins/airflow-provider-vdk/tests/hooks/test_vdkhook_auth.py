# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest import mock

from vdk.plugin.control_api_auth.auth_exception import VDKInvalidAuthParamError
from vdk_provider.hooks.vdk import VDKHook

log = logging.getLogger(__name__)


class TestVDKHookAuth(unittest.TestCase):
    @mock.patch.dict(
        "os.environ",
        AIRFLOW_CONN_CONN_VDK="http://https%3A%2F%2Fwww.vdk-endpoint.org?auth_type=api_token&token=test1token",
    )
    def test_missing_auth_server_from_conn(self):
        with self.assertRaises(
            VDKInvalidAuthParamError,
            msg="VDKInvalidAuthParamError should be raised for missing auth_server in connection.",
        ):
            self.hook = VDKHook(
                conn_id="conn_vdk", job_name="test_job", team_name="test_team"
            )

    @mock.patch.dict(
        "os.environ",
        AIRFLOW_CONN_CONN_VDK="http://https%3A%2F%2Fwww.vdk-endpoint.org?auth_server=example.com&token=test1token",
    )
    def test_missing_auth_type_from_conn(self):
        with self.assertRaises(
            VDKInvalidAuthParamError,
            msg="VDKInvalidAuthParamError should be raised for missing auth_type in connection.",
        ) as exc_info:
            self.hook = VDKHook(
                conn_id="conn_vdk", job_name="test_job", team_name="test_team"
            )

        self.assertIn("auth_type was not specified", exc_info.exception.message)

    @mock.patch.dict(
        "os.environ",
        AIRFLOW_CONN_CONN_VDK="http://https%3A%2F%2Fwww.vdk-endpoint.org?auth_server=example.com&auth_type=wrong_auth&token=test1token",
    )
    def test_missing_unrecognised_auth_type_from_conn(self):
        with self.assertRaises(
            VDKInvalidAuthParamError,
            msg="VDKInvalidAuthParamError should be raised for missing auth_type in connection.",
        ) as exc_info:
            self.hook = VDKHook(
                conn_id="conn_vdk", job_name="test_job", team_name="test_team"
            )

        self.assertIn("Unexpected authentication type", exc_info.exception.message)
