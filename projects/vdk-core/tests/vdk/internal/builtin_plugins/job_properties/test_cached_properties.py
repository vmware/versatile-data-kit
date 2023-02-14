# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import MagicMock

from vdk.api.job_input import IProperties
from vdk.internal.builtin_plugins.job_properties.cached_properties import (
    CachedPropertiesWrapper,
)


class CachedPropertiesWrapperTests(unittest.TestCase):
    def test_caching(self):
        mock_properties = MagicMock(spec=IProperties)
        mock_properties.get_all_properties.return_value = {"a": "aa", "b": "bb"}
        c = CachedPropertiesWrapper(mock_properties)

        self.assertEqual(c.get_property("a"), "aa")
        self.assertEqual(c.get_property("b"), "bb")
        self.assertDictEqual(c.get_all_properties(), {"a": "aa", "b": "bb"})
        self.assertEqual(
            c.get_property("nonexistentproperty", "default value"), "default value"
        )
        c.get_all_properties()
        c.get_all_properties()
        self.assertEqual(
            mock_properties.get_all_properties.call_count, 1
        )  # original properties loaded once, although we queried them many times
        self.assertEqual(
            mock_properties.get_property.call_count, 0
        )  # CachedPropertiesWrapper never calls get_property()
        self.assertEqual(mock_properties.set_all_properties.call_count, 0)

        # test that set_all causes the cached properties to call get_all once more to refresh cache
        c.set_all_properties(
            {}
        )  # the mock will continue to return {'a': 'aa', 'b': 'bb'}
        self.assertEqual(mock_properties.set_all_properties.call_count, 1)
        count = mock_properties.get_all_properties.call_count
        self.assertEqual(c.get_property("a"), "aa")
        self.assertEqual(mock_properties.get_all_properties.call_count, count + 1)
        self.assertEqual(c.get_property("b"), "bb")
        self.assertEqual(
            c.get_property("nonexistentproperty", "default value"), "default value"
        )
        self.assertEqual(mock_properties.get_all_properties.call_count, count + 1)
