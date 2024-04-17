# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging

from vdk.internal.core.errors import VdkConfigurationError
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

# Consider ConfigValue should be primitive type perhaps? and not just any object
ConfigValue = Any
ConfigKey = str

log = logging.getLogger(__name__)


def convert_value_to_type_of_default_type(key: str, v: Any, default_value: Any) -> Any:
    """
    Converts a given configuration value to the type of its default value if a default is provided.

    Args:
        key (str): The key for the configuration setting.
        v (Any): The value to be converted.
        default_value (Any): The default value which defines the type to which the value should be converted.

    Returns:
        Any: The value converted to the type of the default value.

    Raises:
        VdkConfigurationError: If the value cannot be converted to the required type or if an invalid value is provided for a boolean.
    """
    if default_value is not None:
        if isinstance(default_value, bool):
            allowed_values = ["true", "false", "1", "0", "yes", "no", "y", "n"]
            v_str = str(v).lower()
            if v_str not in allowed_values:
                raise VdkConfigurationError(
                    f"Provided configuration '{key}={v}' is invalid. Allowed values for {key} are {allowed_values}"
                )
            return v_str in ["true", "1", "yes", "y"]
        else:
            try:
                return type(default_value)(v)
            except ValueError:
                raise VdkConfigurationError(
                    f'Provided configuration "{key}={v}" is invalid. Cannot cast "{v}" to {type(default_value).__name__}'
                )
    return v


def _normalize_config_string(key: str):
    return str(key).lower()


@dataclass
class ConfigEntry:
    """
    A dataclass to store individual configuration item properties.

    Attributes:
        value: The current value of the configuration item.
        default: The default value of the configuration item.
        description: A string describing the configuration item.
        sensitive: A boolean indicating if the configuration item is sensitive.
    """
    value: Any = None
    default: Any = None
    description: Optional[str] = None
    sensitive: bool = False


@dataclass(frozen=True)
class Configuration:
    """
    The immutable configuration for an application, organized by sections.

    Each section contains configuration entries defined by the ConfigEntry dataclass,
    allowing complex configuration setups with multiple sections, each potentially having
    overlapping key names but distinct settings.

    Attributes:
        __sections (Dict[str, Dict[ConfigKey, ConfigEntry]]): A dictionary where each key is a section name
                                                        and each value is another dictionary mapping
                                                        configuration keys to ConfigEntry instances.
    """
    __sections: Dict[str, Dict[ConfigKey, ConfigEntry]] = field(default_factory=dict)

    def get_value(self, section: str, key: str) -> Optional[Any]:
        """
        Retrieve the current value of a configuration key within a specified section.

        Args:
            section (str): The name of the section.
            key (str): The configuration key.

        Returns:
            Any: The current value of the configuration key if it exists, None otherwise.
        """
        section = _normalize_config_string(section)
        key = _normalize_config_string(key)
        return self.__sections.get(section, {}).get(key, ConfigEntry()).value

    def get_required_value(self, section: str, key: str) -> Any:
        """
        Retrieve the current value of a configuration key within a specified section and raise
        an error if it is not set.

        Args:
            section (str): The name of the section.
            key (str): The configuration key.

        Returns:
            Any: The current value of the configuration key.

        Raises:
            ValueError: If the configuration key is not set.
        """
        section = _normalize_config_string(section)
        key = _normalize_config_string(key)
        value = self.get_value(section, key)
        if value is None:
            raise ValueError(f"Required configuration {key} in section {section} is missing.")
        return value

    def get_description(self, section: str, key: str) -> Optional[str]:
        """
        Retrieve the description of a configuration key within a specified section.

        Args:
            section (str): The name of the section.
            key (str): The configuration key.

        Returns:
            Optional[str]: The description of the configuration key if it exists, None otherwise.
        """
        section = _normalize_config_string(section)
        key = _normalize_config_string(key)
        return self.__sections.get(section, {}).get(key, ConfigEntry()).description

    def is_sensitive(self, section: str, key: str) -> bool:
        """
        Check if a configuration key within a specified section is marked as sensitive.

        Args:
            section (str): The name of the section.
            key (str): The configuration key.

        Returns:
            bool: True if the configuration key is marked as sensitive, False otherwise.
        """
        section = _normalize_config_string(section)
        key = _normalize_config_string(key)
        return self.__sections.get(section, {}).get(key, ConfigEntry()).sensitive


@dataclass
class ConfigurationBuilder:
    """
    A builder class for creating a Configuration object, structured to allow detailed control
    over configuration data organized by sections and keys.

    This builder supports defining complex configurations that can handle multiple sections,
    with each section potentially containing overlapping key names but with distinct settings.

    Attributes:
        __sections (Dict[str, Dict[ConfigKey, ConfigEntry]]): Stores all configuration data during the building process.
                                                Each section maps configuration keys to their respective ConfigEntry.
    """
    __sections: Dict[str, Dict[ConfigKey, ConfigEntry]] = field(default_factory=dict)

    def add(self, section: str, key: str, default_value: Optional[Any] = None, description: Optional[str] = None,
            is_sensitive: bool = False) -> 'ConfigurationBuilder':
        """
        Adds a configuration key with its associated properties to a specified section. If the section does not
        already exist, it is created.

        Args:
            section (str): The name of the section to which the configuration key will be added.
            key (str): The configuration key to add.
            default_value (Optional[Any]): The default value for the configuration key, used if no value is explicitly set.
            description (Optional[str]): A human-readable description of the configuration key.
            is_sensitive (bool): Indicates whether the configuration key contains sensitive information.

        Returns:
            ConfigurationBuilder: Returns the builder instance to enable method chaining.
        """
        section = _normalize_config_string(section)
        key = _normalize_config_string(key)
        self.__add_public(section, key, default_value, description, is_sensitive)
        return self

    def __add_public(self, section: str, key: str, default_value: Optional[Any], description: Optional[str],
                     is_sensitive: bool) -> None:
        """
        Handles the internal logic of adding a new configuration key to a section, including managing descriptions
        and sensitivity settings. This method encapsulates additional formatting and initialization operations
        that are abstracted from the user.

        Args:
            section (str): The name of the section where the key will be added.
            key (str): The configuration key to be added.
            default_value (Optional[Any]): The default value for the configuration key.
            description (Optional[str]): The description of the configuration key; enhances user documentation.
            is_sensitive (bool): Specifies if the configuration key is sensitive.

        Raises:
            ValueError: If the key already exists and the function is intended to only handle new additions.
        """
        section = _normalize_config_string(section)
        key = _normalize_config_string(key)
        if section not in self.__sections:
            self.__sections[section] = {}

        formatted_description = description if description else "No description provided."
        if is_sensitive:
            formatted_description += " This option is marked as sensitive."

        self.__sections[section][key] = ConfigEntry(
            value=default_value,
            default=default_value,
            description=formatted_description,
            sensitive=is_sensitive
        )

    def set_value(self, section: str, key: str, value: Any) -> 'ConfigurationBuilder':
        """
        Sets or updates the value for a specific configuration key within a designated section.

        Args:
            section (str): The name of the section containing the configuration key.
            key (str): The configuration key whose value is to be updated.
            value (Any): The new value to assign to the configuration key.

        Returns:
            ConfigurationBuilder: Returns the builder instance to enable method chaining.

        Raises:
            ValueError: If the key does not exist in the given section, indicating it must be added first.
        """
        section = _normalize_config_string(section)
        key = _normalize_config_string(key)
        if section not in self.__sections or key not in self.__sections[section]:
            raise ValueError(f"Key {key} does not exist in section {section}. Please add it first.")
        default_value = self.__sections[section][key].default
        converted_value = convert_value_to_type_of_default_type(key, value, default_value)
        self.__sections[section][key].value = converted_value
        return self

    def build(self) -> Configuration:
        """
        Finalizes the building process and constructs an immutable Configuration object from the accumulated data.

        Returns:
            Configuration: The constructed immutable configuration object, ready to be used within the application.
        """
        return Configuration(__sections=self.__sections)


