# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import dataclasses

import pytest
from vdk.internal.builtin_plugins.ingestion.source.config import config_class
from vdk.internal.builtin_plugins.ingestion.source.config import config_field
from vdk.internal.builtin_plugins.ingestion.source.config import (
    get_config_field_metadata,
)


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

    metadata = get_config_field_metadata(TestConfig, "attr")
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

    metadata = get_config_field_metadata(TestConfig, "attr")
    assert metadata.default() == 42


def test_config_field_sensitive():
    @config_class("test_name", "test_description")
    class TestConfig:
        attr: bool = config_field(description="attr_description", is_sensitive=True)

    metadata = get_config_field_metadata(TestConfig, "attr")
    assert metadata.is_sensitive() is True


def test_invalid_field_missing_config_field():
    with pytest.raises(TypeError):

        @config_class("test_name", "test_description")
        class TestConfig:
            attr: bool
