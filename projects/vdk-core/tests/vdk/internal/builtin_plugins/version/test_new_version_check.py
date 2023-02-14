# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from http.client import HTTPResponse
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from vdk.internal.builtin_plugins.version.new_version_check import Package


class PackageTests(unittest.TestCase):
    def __mock_http_response(self, body, status):
        class StubHTTPResponse(HTTPResponse):
            def __init__(self, body, status):
                super().__init__(MagicMock())
                self.status = status
                self.body = body

            def read(self) -> bytes:
                return self.body

        return StubHTTPResponse(body, status)

    def test_get_highest_version_from_index(self):
        data = b">vdk-core-1.4.123578<, >vdk-core-1.3.2334367<"

        pkg_obj = Package("vdk-core", "https://test.index.com/api/pypi/simple")
        pkg_obj.http = Mock()
        pkg_obj.http.urlopen.return_value = self.__mock_http_response(
            body=data, status=200
        )

        processed_req = pkg_obj._get_highest_version_from_index()
        self.assertEqual(processed_req, (1, 4, 123578))

    def test_check_highest_from_index(self):
        data = b">vdk-core-1.4.123578<, >vdk-core-1.3.2334367<"

        with patch.object(
            Package, "_get_current", return_value=(1, 4, 112345)
        ) as patched_current:
            pkg_obj = Package("vdk-core", "https://test.index.com/api/pypi/simple")
            pkg_obj.http = Mock()
            pkg_obj.http.urlopen.return_value = self.__mock_http_response(
                body=data, status=200
            )

            self.assertTrue(pkg_obj.check())
        patched_current.assert_called_once()

    def test_ignore_highest_dev_version(self):
        data = b">vdk-core-1.4.123578<, >vdk-core-1.3.2334367<, >vdk-core-1.4.123578.dev1235<"

        with patch.object(
            Package, "_get_current", return_value=(1, 4, 123578)
        ) as patched_current:
            pkg_obj = Package("vdk-core", "https://test.index.com/api/pypi/simple")
            pkg_obj.http = Mock()
            pkg_obj.http.urlopen.return_value = self.__mock_http_response(
                body=data, status=200
            )

            self.assertFalse(pkg_obj.check())
        patched_current.assert_called_once()

    def test_check_highest_version(self):
        with patch.object(
            Package, "_get_current", return_value=(1, 4, 2334367)
        ) as patched_current:
            with patch.object(
                Package, "_get_highest_version_from_index", return_value=(1, 3, 123578)
            ) as patched_highest:
                pkg_obj = Package("vdk-core", "https://test.index.com/api/pypi/simple")
                pkg_obj.http = Mock()

                self.assertFalse(pkg_obj.check())
            patched_current.assert_called_once()
            patched_highest.assert_called_once()

    def test_ver_to_tuple(self):
        pkg_obj = Package("vdk-core", "https://test.index.com/api/pypi/simple")

        self.assertEqual(pkg_obj._ver_to_tuple("1.3.123578"), (1, 3, 123578))
        self.assertEqual(pkg_obj._ver_to_tuple("1.3.123578rc1"), (1, 3, 123578, 1))
        self.assertEqual(pkg_obj._ver_to_tuple("1.3.123578.rc1"), (1, 3, 123578, 1))
        self.assertEqual(pkg_obj._ver_to_tuple("1.3.123578-rc1"), (1, 3, 123578, 1))
        self.assertEqual(pkg_obj._ver_to_tuple("1.3.123578-dev1"), (1, 3, 123578, 1))
