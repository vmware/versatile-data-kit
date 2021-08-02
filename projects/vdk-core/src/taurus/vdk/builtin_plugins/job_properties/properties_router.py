# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.plugin.plugin_input import IPropertiesFactory
from taurus.api.plugin.plugin_input import IPropertiesRegistry
from taurus.vdk.builtin_plugins.job_properties.cached_properties import (
    CachedPropertiesWrapper,
)
from taurus.vdk.builtin_plugins.job_properties.datajobs_service_properties import (
    DataJobsServiceProperties,
)
from taurus.vdk.builtin_plugins.job_properties.properties_config import (
    PropertiesConfiguration,
)
from taurus.vdk.builtin_plugins.job_properties.Propertiesnotavailable import (
    PropertiesNotAvailable,
)
from taurus.vdk.core import errors
from taurus.vdk.core.config import Configuration
from taurus.vdk.util.decorators import LogDecorator

log: logging.Logger = logging.getLogger(__name__)


class PropertiesRouter(IPropertiesRegistry):
    """
    Implements registry of IProperties.
    """

    def __init__(self, job_name: str, cfg: Configuration):
        self.__properties_builders = {}
        self.__cached_properties_impl = None
        self.__job_name = job_name
        self.__config = PropertiesConfiguration(cfg)

    @LogDecorator(log)
    def set_properties_factory_method(
        self, properties_type: str, properties_factory: IPropertiesFactory
    ) -> None:
        self.__properties_builders[properties_type] = properties_factory

    def get_properties_impl(self):
        if not self.__cached_properties_impl:
            if self.__properties_builders:
                self.__cached_properties_impl = (
                    self.__setup_properties_from_factory_method()
                )
            else:
                why = "No properties client implementation has been installed or configured. "
                countermeasures = (
                    "Check if you have installed properly vdk. "
                    "Check if you need to install some plugin for properties. "
                    "If a plugin is installed, check out plugin documentation"
                    " whether the plugin is configured correctly."
                )
                error_handler = self.__properties_not_available_error_handler(
                    why=why, countermeasures=countermeasures
                )
                self.__cached_properties_impl = PropertiesNotAvailable(error_handler)
        return self.__cached_properties_impl

    def __choose_from_default_type(self, properties_type: str):
        if properties_type in self.__properties_builders:
            return self.__properties_builders.get(properties_type)
        else:
            errors.log_and_throw(
                errors.ResolvableBy.CONFIG_ERROR,
                log,
                "",
                f"properties default type was configured to be {properties_type} "
                f"no such properties api implementation has been registered",
                f"",
                f"Check if the job has not been mis-configured - for example misspelling error. "
                f"See config-help for help on configuration. Existing properties types are: {list(self.__properties_builders.keys())} "
                f"Alternatively make sure the correct plugin has been installed "
                f"providing the properties api implementation ",
            )

    def __setup_properties_from_factory_method(self):
        try:
            properties_type = self.__config.get_properties_default_type()
            factory_method = None
            if properties_type:
                factory_method = self.__choose_from_default_type(properties_type)
            elif "default" in self.__properties_builders:
                factory_method = self.__choose_from_default_type("default")
            elif len(self.__properties_builders) == 1:
                factory_method = self.__properties_builders[
                    list(self.__properties_builders.keys())[0]
                ]
            else:
                errors.log_and_throw(
                    errors.ResolvableBy.CONFIG_ERROR,
                    log,
                    "",  # set by handler
                    f"Too many choices.",
                    f"",  # set by handler
                    f"Configure which properties client implementation "
                    f"to use with properties_default_type config option. "
                    f"See config-help for help on configuration. Existing properties types are: {list(self.__properties_builders.keys())}",
                )

            service_properties = DataJobsServiceProperties(
                self.__job_name, factory_method()
            )
            return CachedPropertiesWrapper(service_properties)
        except Exception as e:
            log.warning(
                "Could not build properties provider. "
                "This will result in failure if getting/setting properties is used."
            )
            error_handler = self.__properties_not_available_error_handler(str(e))
            return PropertiesNotAvailable(error_handler)

    @staticmethod
    def __properties_not_available_error_handler(why, countermeasures=None):
        if not countermeasures:
            countermeasures = " Check why it happened and try to resolve the issue or open a ticket to SRE team."

        error_handler = lambda methodname: errors.log_and_throw(
            to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
            log=logging.getLogger(__name__),
            what_happened="I'm trying to call method '{}' and failed.".format(
                methodname
            ),
            why_it_happened=why,
            consequences="Current  Step will fail, and as a result the whole Data Job will fail.",
            countermeasures=countermeasures,
        )
        return error_handler
