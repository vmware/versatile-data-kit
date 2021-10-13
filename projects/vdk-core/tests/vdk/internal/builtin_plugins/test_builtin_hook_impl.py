# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import MagicMock

from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins import builtin_hook_impl
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.internal.core.statestore import StateStore


class TestLocalIdSetting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuration = ConfigurationBuilder().build()
        cls.plugin_registry = MagicMock(spec=IPluginRegistry)
        cls.state = StateStore()

        cls.context = CoreContext(cls.plugin_registry, cls.configuration, cls.state)
        cls.initializer = builtin_hook_impl.RuntimeStateInitializePlugin()
        cls.initializer.vdk_initialize(cls.context)

    def test_auto_generated_execution_id(self):
        assert self.context.state.get(CommonStoreKeys.EXECUTION_ID)

    def test_auto_generated_attempt_id(self):
        assert self.context.state.get(CommonStoreKeys.ATTEMPT_ID)

    def test_auto_generated_op_id(self):
        assert self.context.state.get(CommonStoreKeys.OP_ID) == self.context.state.get(
            CommonStoreKeys.EXECUTION_ID
        )

    def test_execution_id_len(self):
        # job name is uuid 36 chars + - + timestamp 10 chars = 47
        assert len(self.context.state.get(CommonStoreKeys.EXECUTION_ID)) == 47

    def test_op_id_len(self):
        # same as execution_id
        assert len(self.context.state.get(CommonStoreKeys.OP_ID)) == 47

    def test_attempt_id_len(self):
        # execution id len + - + 5 chars = 53
        assert len(self.context.state.get(CommonStoreKeys.ATTEMPT_ID)) == 53


class TestExternalId(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        cls.configuration = (
            ConfigurationBuilder()
            .add("ATTEMPT_ID", "mzhivkov-test-job-1234567890-akmvy")
            .build()
        )
        cls.plugin_registry = MagicMock(spec=IPluginRegistry)
        cls.state = StateStore()

        cls.context = CoreContext(cls.plugin_registry, cls.configuration, cls.state)
        cls.initializer = builtin_hook_impl.RuntimeStateInitializePlugin()
        cls.initializer.vdk_initialize(cls.context)

    def test_execution_id(self):
        assert (
            self.context.state.get(CommonStoreKeys.EXECUTION_ID)
            == "mzhivkov-test-job-1234567890"
        )

    def test_op_id(self):
        assert (
            self.context.state.get(CommonStoreKeys.OP_ID)
            == "mzhivkov-test-job-1234567890"
        )

    def test_attempt_id(self):
        assert (
            self.context.state.get(CommonStoreKeys.ATTEMPT_ID)
            == "mzhivkov-test-job-1234567890-akmvy"
        )
