# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from taurus.vdk.core.errors import VdkConfigurationError

# Consider ConfigValue should be primitive type perhaps? and not just any object
ConfigValue = Any
ConfigKey = str


def convert_value_to_type_of_default_type(
    key: ConfigKey, v: ConfigValue, default_value: ConfigValue
) -> ConfigValue:
    """
    Allows for configurations to be converted to the type of their default value.

    E.g. IMPALA_PORT is converted to int, because it's default value is int.
    """
    if default_value is not None:
        if type(default_value) == type(True) and type(v) != type(True):
            allowed_values = ["true", "false", "1", "0", "yes", "no", "y", "n"]
            if str(v).lower() not in allowed_values:
                msg = (
                    f"Provided configuration "
                    f'"{key}={v}" is invalid. Allowed values for {key} are {allowed_values}'
                )
                raise VdkConfigurationError(msg)
            v = str(v).lower() in ["true", "1", "yes", "y"]
        else:
            try:
                v = type(default_value)(v)  # cast to type of default_value:
            except ValueError:
                msg = (
                    f'Provided configuration "{key}={v}" is invalid. '
                    f'Cannot cast "{v}" to {str(type(default_value).__name__)}'
                )
                raise VdkConfigurationError(msg)
    return v


@dataclass(frozen=True)
class Configuration:
    """
    The configuration of the application. It's immutable.

    Use ConfigurationBuilder to build it.
    """

    config_key_to_description: dict[ConfigKey, str]
    config_key_to_value: dict[ConfigKey, ConfigValue]

    def __getitem__(self, key: ConfigKey):
        return self.get_value(key)

    def get_value(self, key: ConfigKey) -> ConfigValue:
        """
        Return configuration value associated with a given key or None if it does not exists.

        For required configuration see get_required_value

        :param key: the configuration key (e.g db_host, service_uri, etc.)
        :return: the value corresponding to the configuration key
        """
        try:
            return self.config_key_to_value[key]
        except KeyError:
            return None

    def get_required_value(self, key: ConfigKey) -> ConfigValue:
        """
        Return configuration value associated with a given key or throws VdkConfigurationError if it's missing.

        Use get_value if configuration is not required

        :param key: the configuration key (e.g db_host, service_uri, etc.)
        :return: the value corresponding to the configuration key
        :raises VdkConfigurationError
        """
        value = self.get_value(key)
        if value is None:
            raise VdkConfigurationError(
                f"Required configuration {key} is missing."
                f"This will cause configuration error and some functionality may not work."
                f"Please provide correct configuration value. "
                f"See help for how to configure the tool"
            )
        return value

    def get_description(self, key: ConfigKey) -> str | None:
        """
        Get description of hte configuration with that key. It will be used to be printed in help.

        :param key: the config key
        :return: description
        """
        try:
            return self.config_key_to_description.get(key)
        except KeyError:
            return None


@dataclass()
class ConfigurationBuilder:
    """
    Builder used to configure the app.

    Usually a plugin would define what variables it needs using add method.
    While other plugins will populate them using set_value method (e.g environment variable plugin. yaml file plugin, etc.).
    """

    __config_key_to_description: dict[ConfigKey, str]
    __config_key_to_value: dict[ConfigKey, ConfigValue]

    def __init__(self):
        self.__config_key_to_description = OrderedDict()
        self.__config_key_to_value = OrderedDict()

    def add(
        self,
        key: ConfigKey,
        default_value: ConfigValue,
        show_default_value=False,
        description=None,
    ) -> ConfigurationBuilder:
        """
        Add new configuration variable definition.

        :param key: The configuration key. If already exist variable will be updated.
        :param default_value: Default value for the configuration Can be None.
        :param show_default_value: default value will appear in help as well.
        The default value type will enforce the type of the option. Can be None - in this case the type would str.
        :param description: Set description if you want config variable to appear in command line help .
        It is strongly recommended to set description. If no description is set the config key will be hidden.
        TODO: in the future we should require description always and have separate hidden=True/False instead
        :return: self so it can be chained like builder.add(..).set_value(...)...
        """
        self.set_value(key, default_value)
        if description and show_default_value:
            self.__add_public(key, description, default_value)
        elif description:
            self.__add_public(key, description)
        return self

    def set_value(self, key: ConfigKey, value: ConfigValue) -> ConfigurationBuilder:
        """
        This will set or update the value for a configuration with a given key.

        It will try to cast it to the specified default type inferred from default value (set with #add method)
        :param key: the configuration key
        :param value: the configuration value.
        :return: self so it can be chained like builder.set_value(..).add(...)...
        """
        default_value = (
            self.__config_key_to_value.get(key)
            if key in self.__config_key_to_value
            else None
        )
        self.__config_key_to_value[key] = convert_value_to_type_of_default_type(
            key, value, default_value
        )
        return self

    def list_config_keys(self) -> list[ConfigKey]:
        """
        List all added (defined) config keys

        :return: list of key names.
        """
        return [k for k in self.__config_key_to_value.keys()]

    def __add_public(
        self, key: ConfigKey, description: str, default_value: ConfigValue = None
    ) -> None:
        if default_value is not None:
            description += "\nDefault value is: '%s'." % default_value
        self.__config_key_to_description[key] = description

    def build(self) -> Configuration:
        """
        :return: immutable version of the Configuration
        """
        return Configuration(
            self.__config_key_to_description, self.__config_key_to_value
        )
