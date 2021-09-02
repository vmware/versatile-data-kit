# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.core.errors import VdkConfigurationError


@pytest.mark.parametrize(
    "key, default_value, show_default_value, description",
    (
        ("int_key", 1, True, "int key"),
        ("bool_key", True, False, "bool key"),
        ("array_key", [], None, None),
        ("str_key", "string", None, None),
        ("str_key", None, None, None),
    ),
)
def test_add(key, default_value, show_default_value, description):
    builder = ConfigurationBuilder()
    builder.add(key, default_value, show_default_value, description)
    cfg = builder.build()
    assert description is None or description in cfg.get_description(key)
    assert default_value == cfg.get_value(key)
    assert default_value == cfg[key]


def test_unknown_key():
    builder = ConfigurationBuilder()
    builder.add("key", 1)
    builder.add("none-key", None)
    cfg = builder.build()

    with pytest.raises(VdkConfigurationError):
        cfg.get_required_value("no-such-key")
    with pytest.raises(VdkConfigurationError):
        cfg.get_required_value("none-key")

    assert cfg.get_value("no-such-key") is None
    assert cfg["no-such-key"] is None
    assert cfg.get_description("no-such-key") is None

    assert cfg.get_description("key") is None
    assert cfg.get_value("key") == 1


@pytest.mark.parametrize(
    "key, value",
    (
        ("int_key", 1),
        ("bool_key", True),
        ("array_key", []),
        ("str_key", "string"),
    ),
)
def test_set_value(key, value):
    builder = ConfigurationBuilder()
    builder.set_value(key, value)
    cfg = builder.build()
    assert cfg.get_value(key) == value
    assert cfg[key] == value


def test_set_value_overrides_default():
    builder = ConfigurationBuilder()
    builder.set_value("key", "value")
    builder.add("key", "default_value", False, "key description")
    cfg = builder.build()
    assert cfg.get_value("key") == "value"


def test_list_config_keys():
    builder = ConfigurationBuilder()
    builder.add("key1", 1)
    builder.add("key2", "two")
    builder.add("key3", None)
    builder.add("key4", False, False, "description")
    builder.add("key5", 1.2, True, "description")
    assert {"key1", "key2", "key3", "key4", "key5"} == set(builder.list_config_keys())


def test_conversions():
    from taurus.vdk.core import config

    assertEqual(
        "some value",
        config.convert_value_to_type_of_default_type(
            "somekey", "some value", "default value"
        ),
    )
    assertEqual(
        True, config.convert_value_to_type_of_default_type("somekey", "True", False)
    )
    assertEqual(
        True, config.convert_value_to_type_of_default_type("somekey", "yes", False)
    )
    assertEqual(
        True, config.convert_value_to_type_of_default_type("somekey", "Yes", False)
    )
    assertEqual(
        False, config.convert_value_to_type_of_default_type("somekey", "No", True)
    )
    assertEqual(
        False, config.convert_value_to_type_of_default_type("somekey", False, True)
    )
    assertEqual(
        None, config.convert_value_to_type_of_default_type("somekey", None, None)
    )
    assertEqual(
        False, config.convert_value_to_type_of_default_type("somekey", False, None)
    )
    assertEqual(1, config.convert_value_to_type_of_default_type("somekey", "1", 2))

    from taurus.vdk.core.errors import VdkConfigurationError

    with pytest.raises(VdkConfigurationError):  # cannot convert 'x' to int
        config.convert_value_to_type_of_default_type("somekey", "x", 1)

    with pytest.raises(VdkConfigurationError):  # cannot convert 'x' to boolean
        assertEqual(
            "x", config.convert_value_to_type_of_default_type("somekey", "x", True)
        )


def assertEqual(a, b):
    assert a == b
