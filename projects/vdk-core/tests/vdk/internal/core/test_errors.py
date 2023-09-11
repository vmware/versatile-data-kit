# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from collections import defaultdict
from unittest.mock import MagicMock

import pytest
from vdk.internal.core import errors
from vdk.internal.core.errors import PlatformServiceError
from vdk.internal.core.errors import UserCodeError

log = logging.getLogger(__name__)


class ErrorsTest(unittest.TestCase):
    def tearDown(self):
        errors.resolvable_context().clear()

    def test_resolvable_context_singleton(self):
        assert (
            errors.resolvable_context()
            is errors.ResolvableContext()
            is errors.resolvable_context()
            is errors.ResolvableContext()
        )

    def test_get_blamee_overall_none(self):
        blamee = errors.get_blamee_overall()
        self.assertEqual(blamee, None, "There are no errors")

    def test_get_blamee_overall_platform(self):
        try:
            raise Exception()
        except Exception as e:
            errors.report(errors.ResolvableBy.PLATFORM_ERROR, e)
            errors.log_exception(
                log,
                e,
                "something happened",
                "...",
                "XYZ",
                "Think! SRE",
            )
        self.assertEqual(
            errors.get_blamee_overall(), errors.ResolvableByActual.PLATFORM, "Platform"
        )

    def test_get_blamee_overall_owner(self):
        try:
            raise Exception()
        except Exception as e:
            errors.report(errors.ResolvableBy.USER_ERROR, e)
            errors.log_exception(
                log,
                e,
                "something happened",
                "...",
                "XYZ",
                "Think! Owner",
            )
        self.assertEqual(
            errors.get_blamee_overall(), errors.ResolvableByActual.USER, "User"
        )

    def test_get_blamee_overall_both(self):
        try:
            raise Exception()
        except Exception as e:
            errors.report(errors.ResolvableBy.PLATFORM_ERROR, e)
            errors.log_exception(
                log,
                e,
                "something happened",
                "...",
                "XYZ",
                "Think! SRE",
            )
        try:
            raise Exception()
        except Exception as e:
            errors.report(errors.ResolvableBy.USER_ERROR, e)
            errors.log_exception(
                log,
                e,
                "something happened",
                "...",
                "XYZ",
                "Think! Owner",
            )
        self.assertEqual(
            errors.get_blamee_overall(), errors.ResolvableByActual.USER, "User"
        )

    def test_throws_correct_type(self):
        with self.assertRaises(PlatformServiceError) as context:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.PLATFORM_ERROR,
                log=log,
                what_happened="(WHAT)",
                why_it_happened="(WHY)",
                consequences="(CON)",
                countermeasures="(MES)",
            )
        self.assertTrue(isinstance(context.exception, PlatformServiceError))

        with self.assertRaises(UserCodeError) as context:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=log,
                what_happened="(WHAT)",
                why_it_happened="(WHY)",
                consequences="(CON)",
                countermeasures="(MES)",
            )
        self.assertTrue(isinstance(context.exception, errors.UserCodeError))

    def test_exception_matcher_empty_exception(self):
        self.assertTrue(
            errors.exception_matches(
                e=errors.BaseVdkError(""),
                classname_with_package=f"{errors.__name__}.BaseVdkError",
                exception_message_matcher_regex=".*",
            )
        )

    def test_exception_matcher_exception_with_text(self):
        self.assertTrue(
            errors.exception_matches(
                e=errors.BaseVdkError("Some.text.that/should?match!regex"),
                classname_with_package=f"{errors.__name__}.BaseVdkError",
                exception_message_matcher_regex=r".*\..*\..*\/.*\?.*!regex.*",
            )
        )

    def test_exception_matcher_exception_with_wrong_class(self):
        self.assertFalse(
            errors.exception_matches(
                e=errors.BaseVdkError("Doesn't matter what the text is"),
                classname_with_package="wrong.class.package",
                exception_message_matcher_regex="^.*$",
            )
        )

    def test_exception_matche_exception_with_not_matching_message(self):
        self.assertFalse(
            errors.exception_matches(
                e=errors.BaseVdkError("This string doesn't contain question mark"),
                classname_with_package=f"{errors.__name__}.DomainError",
                exception_message_matcher_regex=r"^.*\?.*$",
            )
        )

    def test_report_and_rethrow(self):
        with pytest.raises(IndexError):
            errors.report_and_rethrow(
                errors.ResolvableBy.USER_ERROR,
                exception=IndexError("foo"),
            )
        assert errors.ResolvableByActual.USER in errors.resolvable_context().resolvables
        assert (
            len(errors.resolvable_context().resolvables[errors.ResolvableByActual.USER])
            is 1
        )

    def test_report_and_throw(self):
        with pytest.raises(errors.PlatformServiceError):
            errors.report_and_throw(PlatformServiceError("My super awesome message"))
        assert (
            errors.ResolvableByActual.PLATFORM
            in errors.resolvable_context().resolvables
        )
        assert (
            len(
                errors.resolvable_context().resolvables[
                    errors.ResolvableByActual.PLATFORM
                ]
            )
            is 1
        )
