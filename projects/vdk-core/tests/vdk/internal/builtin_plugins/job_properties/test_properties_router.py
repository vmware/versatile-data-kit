# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock

import pytest
from vdk.api.plugin.plugin_input import IPropertiesServiceClient
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.job_properties.properties_router import (
    PropertiesRouter,
)
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError


def test_routing():
    router = PropertiesRouter(
        "foo", Configuration({}, {JobConfigKeys.TEAM: "test-team"})
    )
    mock_client = MagicMock(spec=IPropertiesServiceClient)
    router.set_properties_factory_method("default", lambda: mock_client)

    router.set_all_properties({"a": "b"})
    mock_client.write_properties.assert_called_with("foo", "test-team", {"a": "b"})

    router.get_all_properties()
    mock_client.read_properties.assert_called_with("foo", "test-team")


def test_routing_error():
    router = PropertiesRouter("foo", Configuration({}, {}))

    def raise_error():
        raise AttributeError("dummy exception")

    router.set_properties_factory_method("default", raise_error)

    with pytest.raises(VdkConfigurationError):
        router.set_all_properties({"a": "b"})


def test_routing_empty_error():
    router = PropertiesRouter("foo", Configuration({}, {}))

    with pytest.raises(VdkConfigurationError):
        router.set_all_properties({"a": "b"})


def test_routing_choose_single_registered():
    router = PropertiesRouter("foo", Configuration({}, {"team": "test-team"}))
    mock_client = MagicMock(spec=IPropertiesServiceClient)
    router.set_properties_factory_method("foo", lambda: mock_client)

    router.set_all_properties({"a": "b"})
    mock_client.write_properties.assert_called_with("foo", "test-team", {"a": "b"})


def test_routing_choose_default_type_chosen():
    router = PropertiesRouter(
        "foo", Configuration({}, {"properties_default_type": "foo"})
    )
    foo_mock_client = MagicMock(spec=IPropertiesServiceClient)
    bar_mock_client = MagicMock(spec=IPropertiesServiceClient)
    router.set_properties_factory_method("foo", lambda: foo_mock_client)
    router.set_properties_factory_method("bar", lambda: bar_mock_client)

    router.set_all_properties({"a": "b"})
    foo_mock_client.write_properties.assert_called_with("foo", None, {"a": "b"})
    bar_mock_client.assert_not_called()


def test_routing_choose_too_many_choices():
    router = PropertiesRouter("foo", Configuration({}, {}))
    foo_mock_client = MagicMock(spec=IPropertiesServiceClient)
    bar_mock_client = MagicMock(spec=IPropertiesServiceClient)
    router.set_properties_factory_method("foo", lambda: foo_mock_client)
    router.set_properties_factory_method("bar", lambda: bar_mock_client)

    with pytest.raises(VdkConfigurationError):
        router.set_all_properties({"a": "b"})


def test_preprocessing_sequence_success():
    router = PropertiesRouter(
        "foo",
        Configuration(
            {},
            {
                JobConfigKeys.TEAM: "test-team",
                "properties_default_type": "foo",
                "properties_write_preprocess_sequence": "bar1,bar2",
            },
        ),
    )
    foo_mock_client = MagicMock(spec=IPropertiesServiceClient)
    bar1_mock_client = MagicMock(spec=IPropertiesServiceClient)
    bar1_mock_client.write_properties.return_value = {"a1": "b1"}
    bar2_mock_client = MagicMock(spec=IPropertiesServiceClient)
    bar2_mock_client.write_properties.return_value = {"a2": "b2"}
    router.set_properties_factory_method("foo", lambda: foo_mock_client)
    router.set_properties_factory_method("bar1", lambda: bar1_mock_client)
    router.set_properties_factory_method("bar2", lambda: bar2_mock_client)

    router.set_all_properties({"a": "b"})
    bar1_mock_client.write_properties.assert_called_with("foo", "test-team", {"a": "b"})
    bar2_mock_client.write_properties.assert_called_with(
        "foo", "test-team", {"a1": "b1"}
    )
    foo_mock_client.write_properties.assert_called_with(
        "foo", "test-team", {"a2": "b2"}
    )


def test_preprocessing_sequence_success_outerscope_immutable():
    router = PropertiesRouter(
        "foo",
        Configuration(
            {},
            {
                JobConfigKeys.TEAM: "test-team",
                "properties_default_type": "foo",
                "properties_write_preprocess_sequence": "bar",
            },
        ),
    )
    foo_mock_client = MagicMock(spec=IPropertiesServiceClient)
    bar_mock_client = MagicMock(spec=IPropertiesServiceClient)
    bar_mock_client.write_properties.return_value = {"a1": "b1"}

    router.set_properties_factory_method("foo", lambda: foo_mock_client)
    router.set_properties_factory_method("bar", lambda: bar_mock_client)

    properties_outer = {"a": "b"}
    router.set_all_properties(properties_outer)
    bar_mock_client.write_properties.assert_called_with("foo", "test-team", {"a": "b"})
    foo_mock_client.write_properties.assert_called_with(
        "foo", "test-team", {"a1": "b1"}
    )
    assert properties_outer == {"a": "b"}


def test_preprocessing_sequence_error():
    router = PropertiesRouter(
        "foo",
        Configuration(
            {},
            {
                JobConfigKeys.TEAM: "test-team",
                "properties_default_type": "foo",
                "properties_write_preprocess_sequence": "bar",
            },
        ),
    )
    foo_mock_client = MagicMock(spec=IPropertiesServiceClient)
    bar_mock_client = MagicMock(spec=IPropertiesServiceClient)
    bar_mock_client.write_properties.side_effect = Exception()
    router.set_properties_factory_method("foo", lambda: foo_mock_client)
    router.set_properties_factory_method("bar", lambda: bar_mock_client)

    with pytest.raises(UserCodeError):
        router.set_all_properties({"a": "b"})


def test_preprocessing_sequence_misconfigured():
    router = PropertiesRouter(
        "foo",
        Configuration(
            {},
            {
                "properties_default_type": "foo",
                "properties_write_preprocess_sequence": "bar",
            },
        ),
    )
    foo_mock_client = MagicMock(spec=IPropertiesServiceClient)
    router.set_properties_factory_method("foo", lambda: foo_mock_client)

    with pytest.raises(VdkConfigurationError):
        router.set_all_properties({"a": "b"})
