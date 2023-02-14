# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest

from vdk.internal.builtin_plugins.job_properties.datajobs_service_properties import (
    DataJobsServiceProperties,
)
from vdk.internal.builtin_plugins.job_properties.inmemproperties import (
    InMemPropertiesServiceClient,
)


class DataJobsServicePropertiesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_jobs_service_props = DataJobsServiceProperties(
            "foo", "test-team", InMemPropertiesServiceClient()
        )

    def test_data_jobs_service_properties_not_allowed_keys(self):
        with self.assertRaises(Exception):
            self.data_jobs_service_props.set_all_properties(
                {" key_with_extra_spaces": "value"}
            )
        with self.assertRaises(Exception):
            self.data_jobs_service_props.set_all_properties(
                {"key with spaces": "value"}
            )
        with self.assertRaises(Exception):
            self.data_jobs_service_props.set_all_properties(
                {1234: "value"}
            )  # non-string type key

    def test_data_jobs_service_properties_allowed_keys(self):
        self.data_jobs_service_props.set_all_properties({"words": "value"})
        self.data_jobs_service_props.set_all_properties({"123": "value"})
        self.data_jobs_service_props.set_all_properties({"a.dot": "value"})
        self.data_jobs_service_props.set_all_properties({"a_underscore": "value"})
        self.data_jobs_service_props.set_all_properties({"a-dash": "value"})

    def test_data_jobs_service_properties_not_allowed_values(self):
        with self.assertRaises(Exception):  # objects not allowed
            self.data_jobs_service_props.set_all_properties({"key": object()})
        with self.assertRaises(Exception):  # byte arrays not allowed
            self.data_jobs_service_props.set_all_properties({"key": bytearray()})

    def test_data_jobs_service_properties_allowed_values(self):
        self.data_jobs_service_props.set_all_properties({"key": 1})
        self.data_jobs_service_props.set_all_properties({"key": "str"})
        self.data_jobs_service_props.set_all_properties({"key": 3.14})
        self.data_jobs_service_props.set_all_properties({"key": "unicode"})
        self.data_jobs_service_props.set_all_properties({"key": r"raw"})
        self.data_jobs_service_props.set_all_properties({"key": None})
        self.data_jobs_service_props.set_all_properties({"key": dict()})

    def test_data_jobs_service_properties(self):
        self.assertEqual(
            self.data_jobs_service_props.get_property("nonexistentproperty"), None
        )
        self.assertEqual(
            self.data_jobs_service_props.get_property(
                "nonexistentproperty", "default value"
            ),
            "default value",
        )

        self.data_jobs_service_props.set_all_properties(
            {"key1": "value1", "key2": dict()}
        )
        self.assertEqual(self.data_jobs_service_props.get_property("key1"), "value1")
        self.assertEqual(self.data_jobs_service_props.get_property("key2"), dict())
        self.assertEqual(
            self.data_jobs_service_props.get_all_properties(),
            {"key1": "value1", "key2": dict()},
        )
