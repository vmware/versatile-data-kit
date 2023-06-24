# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import MagicMock

from vdk.api.job_input import ISecrets
from vdk.internal.builtin_plugins.job_secrets.cached_secrets import (
    CachedSecretsWrapper,
)


class CachedSecrtsWrapperTests(unittest.TestCase):
    def test_caching(self):
        mock_secrets = MagicMock(spec=ISecrets)
        mock_secrets.get_all_secrets.return_value = {"a": "aa", "b": "bb"}
        c = CachedSecretsWrapper(mock_secrets)

        self.assertEqual(c.get_secret("a"), "aa")
        self.assertEqual(c.get_secret("b"), "bb")
        self.assertDictEqual(c.get_all_secrets(), {"a": "aa", "b": "bb"})
        self.assertEqual(
            c.get_secret("nonexistentsecret", "default value"), "default value"
        )
        c.get_all_secrets()
        c.get_all_secrets()
        self.assertEqual(
            mock_secrets.get_all_secrets.call_count, 1
        )  # original secrets loaded once, although we queried them many times
        self.assertEqual(
            mock_secrets.get_secret.call_count, 0
        )  # CachedSecretsWrapper never calls get_secret()
        self.assertEqual(mock_secrets.set_all_secrets.call_count, 0)

        # test that set_all causes the cached secrets to call get_all once more to refresh cache
        c.set_all_secrets({})  # the mock will continue to return {'a': 'aa', 'b': 'bb'}
        self.assertEqual(mock_secrets.set_all_secrets.call_count, 1)
        count = mock_secrets.get_all_secrets.call_count
        self.assertEqual(c.get_secret("a"), "aa")
        self.assertEqual(mock_secrets.get_all_secrets.call_count, count + 1)
        self.assertEqual(c.get_secret("b"), "bb")
        self.assertEqual(
            c.get_secret("nonexistentsecret", "default value"), "default value"
        )
        self.assertEqual(mock_secrets.get_all_secrets.call_count, count + 1)
