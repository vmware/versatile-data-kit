# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import pytest
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.errors import VdkConfigurationError


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
    assert cfg.is_default(key)


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

    assert cfg.get_description("key") == "No description provided. Default value: 1."
    assert cfg.get_value("key") == 1


def test_key_case_insensitive():
    builder = ConfigurationBuilder()
    builder.add("key_1", 1)
    builder.add("key_2", 2)
    builder.set_value("KEY_1", 11)

    cfg = builder.build()

    assert cfg.get_value("key_1") == 11
    assert cfg.get_value("KEY_1") == 11
    assert cfg.get_value("Key_1") == 11
    assert cfg.get_value("key_2") == 2
    assert cfg.get_value("KEY_2") == 2


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
    assert not cfg.is_default("key")


def test_set_value_eq_default_is_default():
    builder = ConfigurationBuilder()
    builder.add("key", "value", False, "key description")
    builder.set_value("key", "value")
    cfg = builder.build()
    assert cfg.get_value("key") == "value"
    assert cfg.is_default("key")


def test_set_value_overrides_default_preserve_types():
    builder = ConfigurationBuilder()
    builder.set_value("key", "False")
    builder.add("key", True, False, "key description")
    builder.set_value("float", "11.12")
    builder.add("float", 1.1, False, "key description")
    cfg = builder.build()
    assert cfg.get_value("key") == False
    assert cfg.get_value("float") == 11.12

    builder.set_value("int", "bad-value")
    with pytest.raises(VdkConfigurationError):
        builder.add("int", 1, False, "key description")


def test_conversions():
    from vdk.internal.core import config

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

    from vdk.internal.core.errors import VdkConfigurationError

    with pytest.raises(VdkConfigurationError):  # cannot convert 'x' to int
        config.convert_value_to_type_of_default_type("somekey", "x", 1)

    with pytest.raises(VdkConfigurationError):  # cannot convert 'x' to boolean
        assertEqual(
            "x", config.convert_value_to_type_of_default_type("somekey", "x", True)
        )


def assertEqual(a, b):
    assert a == b
