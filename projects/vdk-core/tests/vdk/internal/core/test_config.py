# Copyright 2023-2025 Broadcom
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


@pytest.mark.parametrize(
    "section, key, value, description",
    [
        ("section1", "key1", 100, "Description for key1 in section1"),
        ("section1", "key2", 200, "Description for key2 in section1"),
        ("section2", "key1", 300, "Description for key1 in section2"),
        ("section2", "key2", 400, "Description for key2 in section2"),
        ("section3", "key1", 500, "Description for key1 in section3"),
    ],
)
def test_add_with_sections(section, key, value, description):
    builder = ConfigurationBuilder()
    builder.add(
        key=key,
        default_value=value,
        show_default_value=False,
        description=description,
        section=section,
    )
    config = builder.build()

    assert config.get_value(key, section) == value
    assert config.get_description(key, section) == description


def test_non_existent_section():
    builder = ConfigurationBuilder()
    builder.add("key1", 100, section="existent")
    config = builder.build()

    assert config.get_value("key1", "nonexistent") is None


def test_section_isolation():
    builder = ConfigurationBuilder()
    builder.add("key1", 100, section="section1")
    builder.add("key1", 200, section="section2")
    config = builder.build()

    assert config.get_value("key1", "section1") == 100
    assert config.get_value("key1", "section2") == 200

    assert config.list_keys_in_section("section1") == ["key1"]
    assert config.list_keys_in_section("section2") == ["key1"]


def test_sensitive_keys_across_sections():
    builder = ConfigurationBuilder()
    builder.add("key1", "password123", is_sensitive=True, section="secure")
    builder.add("key1", "not-sensitive", is_sensitive=False, section="general")
    config = builder.build()

    assert config.is_sensitive("key1", "secure")
    assert not config.is_sensitive("key1", "general")


@pytest.mark.parametrize(
    "section, key, initial_value, new_value, expected_default",
    [
        ("default_section", "overwrite_key", 150, 250, False),
        ("default_section", "single_key", 350, 350, False),
    ],
)
def test_overwrite_values(section, key, initial_value, new_value, expected_default):
    builder = ConfigurationBuilder()
    builder.add(key, initial_value, section=section)
    builder.set_value(key, new_value, section=section)
    config = builder.build()

    assert config.get_value(key, section) == new_value
    assert config.is_default(key, section) == expected_default


def test_list_sections_and_keys():
    builder = ConfigurationBuilder()
    builder.add("key1", 100, section="section1")
    builder.add("key2", 200, section="section1")
    builder.add("key3", 300, section="section2")
    config = builder.build()

    assert set(config.list_sections()) == {"vdk", "section1", "section2"}
    assert set(config.list_keys_in_section("section1")) == {"key1", "key2"}
    assert set(config.list_keys_in_section("section2")) == {"key3"}
    assert set(config.list_keys_in_section("vdk")) == set()


def test_get_value_without_section():  # fetch from the vdk section by default
    builder = ConfigurationBuilder()
    builder.add("main_key", "section_value", section="local")
    builder.add("main_key", "main_value")
    config = builder.build()

    assert config.get_value("main_key") == "main_value"


def test_missing_key_across_sections():
    builder = ConfigurationBuilder()
    builder.add("unique_key", 123, section="unique_section")
    config = builder.build()

    nevalue = config.get_value("nonexistent_key")
    assert nevalue is None


@pytest.mark.parametrize(
    "key, value, section",
    [("user_setting", True, "user_prefs"), ("system_setting", False, "system_configs")],
)
def test_add_multiple_keys_same_name_different_sections(key, value, section):
    builder = ConfigurationBuilder()
    builder.add(key, value, section=section)
    config = builder.build()

    assert config.get_value(key, section) == value


# sections starting with vdk_ are considered subsections for vdk and are handled differenly
# that's why we introduce separate tests for them


@pytest.mark.parametrize(
    "section, key, value, expected",
    [
        ("vdk_test_db", "connection_string", "test-server-url", "test-server-url"),
        ("vdk_prod_db", "connection_string", "prod-server-url", "prod-server-url"),
        ("vdk_test_db", "max_connections", 10, 10),
        ("vdk_prod_db", "max_connections", 100, 100),
    ],
)
def test_add_and_retrieve_db_configurations(section, key, value, expected):
    builder = ConfigurationBuilder()
    builder.add(key, value, section=section)
    config = builder.build()

    assert config.get_value(key, section) == expected


def test_ensure_environment_isolation():
    builder = ConfigurationBuilder()
    builder.add("timeout", 30, section="vdk_test_db")
    builder.add("timeout", 300, section="vdk_prod_db")
    config = builder.build()

    assert config.get_value("timeout", "vdk_test_db") == 30
    assert config.get_value("timeout", "vdk_prod_db") == 300


def test_access_db_config_without_section_specified():
    builder = ConfigurationBuilder()
    builder.add("cache_enabled", True, section="vdk_test_db")
    config = builder.build()

    # no access to options in vdk subsections without specifying the subsection
    assert config.get_value("cache_enabled") is None


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

    assertEqual(None, config.convert_value_to_type_of_default_type("somekey", None, 2))
    assertEqual(
        None,
        config.convert_value_to_type_of_default_type("somekey", None, "something"),
    )

    from vdk.internal.core.errors import VdkConfigurationError

    with pytest.raises(VdkConfigurationError):  # cannot convert 'x' to int
        config.convert_value_to_type_of_default_type("somekey", "x", 1)

    with pytest.raises(VdkConfigurationError):  # cannot convert 'x' to boolean
        assertEqual(
            "x", config.convert_value_to_type_of_default_type("somekey", "x", True)
        )


def assertEqual(a, b):
    assert a == b
