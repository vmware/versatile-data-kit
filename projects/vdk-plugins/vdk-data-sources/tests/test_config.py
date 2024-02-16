# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass

import pytest
from vdk.plugin.data_sources import config
from vdk.plugin.data_sources.config import config_class
from vdk.plugin.data_sources.config import config_field
from vdk.plugin.data_sources.config import ConfigClassMetadata


def test_config_class():
    @config_class("test_name", "test_description")
    class TestConfig:
        pass

    assert hasattr(TestConfig, "config_group_name")
    assert TestConfig.config_group_name == "test_name"
    assert hasattr(TestConfig, "config_group_description")
    assert TestConfig.config_group_description == "test_description"


def test_config_field_without_default():
    @config_class("test_name", "test_description")
    class TestConfig:
        attr: int = config_field(description="attr_description")

    fields = ConfigClassMetadata(TestConfig).get_config_fields()
    assert len(fields) == 1
    metadata = fields[0]
    assert metadata.name() == "attr"
    assert metadata.description() == "attr_description"
    assert metadata.is_sensitive() is False
    assert metadata.default() is None


def test_config_field_with_default():
    @config_class("test_name", "test_description")
    class TestConfig:
        attr: int = config_field(description="attr_description", default=42)

    instance = TestConfig()
    assert instance.attr == 42

    instance = TestConfig(1)
    assert instance.attr == 1

    metadata = ConfigClassMetadata(TestConfig).get_config_fields()[0]
    assert metadata.name() == "attr"
    assert metadata.default() == 42


def test_config_field_sensitive():
    @config_class("test_name", "test_description")
    class TestConfig:
        attr: bool = config_field(description="attr_description", is_sensitive=True)

    metadata = ConfigClassMetadata(TestConfig).get_config_fields()[0]
    assert metadata.name() == "attr"
    assert metadata.is_sensitive() is True


def test_invalid_field_missing_config_field():
    with pytest.raises(TypeError):

        @config_class("test_name", "test_description")
        class TestConfig:
            attr: bool


def test_deserialize():
    @dataclass
    class SubTest:
        id: str
        num: int

    @config_class("name", "description")
    class Test:
        name: str = config_field(description="foo")
        sub_test: SubTest = config_field(description="subtest")

    actual_instance: Test = config.create_config_from_dict(
        Test, dict(name="my-name", sub_test=dict(id="my-id", num=12))
    )
    assert actual_instance.name == "my-name"
    assert actual_instance.sub_test.id == "my-id"
    assert actual_instance.sub_test.num == 12
