# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest

from vdk.internal.builtin_plugins.job_secrets.datajobs_service_secrets import (
    DataJobsServiceSecrets,
)
from vdk.internal.builtin_plugins.job_secrets.inmemsecrets import (
    InMemSecretsServiceClient,
)


class DataJobsServiceSecretsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_jobs_service_secrets = DataJobsServiceSecrets(
            "foo", "test-team", InMemSecretsServiceClient()
        )

    def test_data_jobs_service_secrets_not_allowed_keys(self):
        with self.assertRaises(Exception):
            self.data_jobs_service_secrets.set_all_secrets(
                {" key_with_extra_spaces": "value"}
            )
        with self.assertRaises(Exception):
            self.data_jobs_service_secrets.set_all_secrets({"key with spaces": "value"})
        with self.assertRaises(Exception):
            self.data_jobs_service_secrets.set_all_secrets(
                {1234: "value"}
            )  # non-string type key

    def test_data_jobs_service_secrets_allowed_keys(self):
        self.data_jobs_service_secrets.set_all_secrets({"words": "value"})
        self.data_jobs_service_secrets.set_all_secrets({"123": "value"})
        self.data_jobs_service_secrets.set_all_secrets({"a.dot": "value"})
        self.data_jobs_service_secrets.set_all_secrets({"a_underscore": "value"})
        self.data_jobs_service_secrets.set_all_secrets({"a-dash": "value"})

    def test_data_jobs_service_secrets_not_allowed_values(self):
        with self.assertRaises(Exception):  # objects not allowed
            self.data_jobs_service_secrets.set_all_secrets({"key": object()})
        with self.assertRaises(Exception):  # byte arrays not allowed
            self.data_jobs_service_secrets.set_all_secrets({"key": bytearray()})

    def test_data_jobs_service_secrets_allowed_values(self):
        self.data_jobs_service_secrets.set_all_secrets({"key": 1})
        self.data_jobs_service_secrets.set_all_secrets({"key": "str"})
        self.data_jobs_service_secrets.set_all_secrets({"key": 3.14})
        self.data_jobs_service_secrets.set_all_secrets({"key": "unicode"})
        self.data_jobs_service_secrets.set_all_secrets({"key": r"raw"})
        self.data_jobs_service_secrets.set_all_secrets({"key": None})
        self.data_jobs_service_secrets.set_all_secrets({"key": dict()})

    def test_data_jobs_service_secrets(self):
        self.assertEqual(
            self.data_jobs_service_secrets.get_secret("nonexistentsecret"), None
        )
        self.assertEqual(
            self.data_jobs_service_secrets.get_secret(
                "nonexistentsecret", "default value"
            ),
            "default value",
        )

        self.data_jobs_service_secrets.set_all_secrets(
            {"key1": "value1", "key2": dict()}
        )
        self.assertEqual(self.data_jobs_service_secrets.get_secret("key1"), "value1")
        self.assertEqual(self.data_jobs_service_secrets.get_secret("key2"), dict())
        self.assertEqual(
            self.data_jobs_service_secrets.get_all_secrets(),
            {"key1": "value1", "key2": dict()},
        )
