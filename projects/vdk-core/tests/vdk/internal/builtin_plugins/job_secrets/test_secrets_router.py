# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock

import pytest
from vdk.api.plugin.plugin_input import ISecretsServiceClient
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.job_secrets.exception import (
    WritePreProcessSecretsException,
)
from vdk.internal.builtin_plugins.job_secrets.secrets_router import (
    SecretsRouter,
)
from vdk.internal.core import errors
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import ResolvableBy
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError


def test_routing():
    router = SecretsRouter("foo", Configuration({}, {JobConfigKeys.TEAM: "test-team"}))
    mock_client = MagicMock(spec=ISecretsServiceClient)
    router.set_secrets_factory_method("default", lambda: mock_client)

    router.set_all_secrets({"a": "b"})
    mock_client.write_secrets.assert_called_with("foo", "test-team", {"a": "b"})

    router.get_all_secrets()
    mock_client.read_secrets.assert_called_with("foo", "test-team")


def test_routing_error():
    router = SecretsRouter("foo", Configuration({}, {}))

    def raise_error():
        raise AttributeError("dummy exception")

    router.set_secrets_factory_method("default", raise_error)

    with pytest.raises(VdkConfigurationError):
        router.set_all_secrets({"a": "b"})


def test_routing_empty_error():
    router = SecretsRouter("foo", Configuration({}, {}))

    with pytest.raises(VdkConfigurationError):
        router.set_all_secrets({"a": "b"})


def test_routing_choose_single_registered():
    router = SecretsRouter("foo", Configuration({}, {"team": "test-team"}))
    mock_client = MagicMock(spec=ISecretsServiceClient)
    router.set_secrets_factory_method("foo", lambda: mock_client)

    router.set_all_secrets({"a": "b"})
    mock_client.write_secrets.assert_called_with("foo", "test-team", {"a": "b"})


def test_routing_choose_default_type_chosen():
    router = SecretsRouter("foo", Configuration({}, {"secrets_default_type": "foo"}))
    foo_mock_client = MagicMock(spec=ISecretsServiceClient)
    bar_mock_client = MagicMock(spec=ISecretsServiceClient)
    router.set_secrets_factory_method("foo", lambda: foo_mock_client)
    router.set_secrets_factory_method("bar", lambda: bar_mock_client)

    router.set_all_secrets({"a": "b"})
    foo_mock_client.write_secrets.assert_called_with("foo", None, {"a": "b"})
    bar_mock_client.assert_not_called()


def test_routing_choose_too_many_choices():
    router = SecretsRouter("foo", Configuration({}, {}))
    foo_mock_client = MagicMock(spec=ISecretsServiceClient)
    bar_mock_client = MagicMock(spec=ISecretsServiceClient)
    router.set_secrets_factory_method("foo", lambda: foo_mock_client)
    router.set_secrets_factory_method("bar", lambda: bar_mock_client)

    with pytest.raises(VdkConfigurationError):
        router.set_all_secrets({"a": "b"})


def test_preprocessing_sequence_success():
    router = SecretsRouter(
        "foo",
        Configuration(
            {},
            {
                JobConfigKeys.TEAM: "test-team",
                "secrets_default_type": "foo",
                "secrets_write_preprocess_sequence": "bar1,bar2",
            },
        ),
    )
    foo_mock_client = MagicMock(spec=ISecretsServiceClient)
    bar1_mock_client = MagicMock(spec=ISecretsServiceClient)
    bar1_mock_client.write_secrets.return_value = {"a1": "b1"}
    bar2_mock_client = MagicMock(spec=ISecretsServiceClient)
    bar2_mock_client.write_secrets.return_value = {"a2": "b2"}
    router.set_secrets_factory_method("foo", lambda: foo_mock_client)
    router.set_secrets_factory_method("bar1", lambda: bar1_mock_client)
    router.set_secrets_factory_method("bar2", lambda: bar2_mock_client)

    router.set_all_secrets({"a": "b"})
    bar1_mock_client.write_secrets.assert_called_with("foo", "test-team", {"a": "b"})
    bar2_mock_client.write_secrets.assert_called_with("foo", "test-team", {"a1": "b1"})
    foo_mock_client.write_secrets.assert_called_with("foo", "test-team", {"a2": "b2"})


def test_preprocessing_sequence_success_outerscope_immutable():
    router = SecretsRouter(
        "foo",
        Configuration(
            {},
            {
                JobConfigKeys.TEAM: "test-team",
                "secrets_default_type": "foo",
                "secrets_write_preprocess_sequence": "bar",
            },
        ),
    )
    foo_mock_client = MagicMock(spec=ISecretsServiceClient)
    bar_mock_client = MagicMock(spec=ISecretsServiceClient)
    bar_mock_client.write_secrets.return_value = {"a1": "b1"}

    router.set_secrets_factory_method("foo", lambda: foo_mock_client)
    router.set_secrets_factory_method("bar", lambda: bar_mock_client)

    secrets_outer = {"a": "b"}
    router.set_all_secrets(secrets_outer)
    bar_mock_client.write_secrets.assert_called_with("foo", "test-team", {"a": "b"})
    foo_mock_client.write_secrets.assert_called_with("foo", "test-team", {"a1": "b1"})
    assert secrets_outer == {"a": "b"}


def test_preprocessing_sequence_error():
    router = SecretsRouter(
        "foo",
        Configuration(
            {},
            {
                JobConfigKeys.TEAM: "test-team",
                "secrets_default_type": "foo",
                "secrets_write_preprocess_sequence": "bar",
            },
        ),
    )
    foo_mock_client = MagicMock(spec=ISecretsServiceClient)
    bar_mock_client = MagicMock(spec=ISecretsServiceClient)
    bar_mock_client.write_secrets.side_effect = Exception()
    router.set_secrets_factory_method("foo", lambda: foo_mock_client)
    router.set_secrets_factory_method("bar", lambda: bar_mock_client)

    with pytest.raises(WritePreProcessSecretsException) as exc_info:
        router.set_all_secrets({"a": "b"})
        assert (
            errors.get_exception_resolvable_by(exc_info.value)
            == ResolvableBy.USER_ERROR
        )


def test_preprocessing_sequence_misconfigured():
    router = SecretsRouter(
        "foo",
        Configuration(
            {},
            {
                "secrets_default_type": "foo",
                "secrets_write_preprocess_sequence": "bar",
            },
        ),
    )
    foo_mock_client = MagicMock(spec=ISecretsServiceClient)
    router.set_secrets_factory_method("foo", lambda: foo_mock_client)

    with pytest.raises(VdkConfigurationError):
        router.set_all_secrets({"a": "b"})
