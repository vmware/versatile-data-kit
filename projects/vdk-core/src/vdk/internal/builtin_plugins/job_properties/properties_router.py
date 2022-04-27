# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any

from vdk.api.job_input import IProperties
from vdk.api.plugin.plugin_input import IPropertiesFactory
from vdk.api.plugin.plugin_input import IPropertiesRegistry
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.job_properties.cached_properties import (
    CachedPropertiesWrapper,
)
from vdk.internal.builtin_plugins.job_properties.datajobs_service_properties import (
    DataJobsServiceProperties,
)
from vdk.internal.builtin_plugins.job_properties.properties_config import (
    PropertiesConfiguration,
)
from vdk.internal.builtin_plugins.job_properties.propertiesnotavailable import (
    PropertiesNotAvailable,
)
from vdk.internal.core import errors
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import ResolvableBy
from vdk.internal.util.decorators import LogDecorator

log: logging.Logger = logging.getLogger(__name__)


class PropertiesRouter(IPropertiesRegistry, IProperties):
    """
    Implements registry of IProperties.
    """

    def __init__(self, job_name: str, cfg: Configuration):
        self.__properties_builders = {}
        self.__cached_properties_impl = None
        self.__job_name = job_name
        self.__team_name = cfg.get_value(JobConfigKeys.TEAM.value)
        self.__config = PropertiesConfiguration(cfg)

    @LogDecorator(log)
    def set_properties_factory_method(
        self, properties_type: str, properties_factory: IPropertiesFactory
    ) -> None:
        self.__properties_builders[properties_type] = properties_factory

    def get_property(self, name: str, default_value: Any = None) -> str:
        return self.__get_properties_impl().get_property(name, default_value)

    def get_all_properties(self) -> dict:
        return self.__get_properties_impl().get_all_properties()

    def set_all_properties(self, properties: dict):
        self.__get_properties_impl().set_all_properties(properties)

    def has_properties_impl(self) -> bool:
        """
        If any properties implementation backend available
        :return: bool
        """
        return not isinstance(self.__get_properties_impl(), PropertiesNotAvailable)

    def __get_properties_impl(self):
        """
        Singleton properties backend implementation.
        """
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
                    "Properties API client cannot be chosen.",  # set by handler
                    f"Too many choices for properties client implementation.",
                    f"Properties API functionality does not work.",  # set by handler
                    f"Configure which properties client implementation "
                    f"to use with properties_default_type config option. "
                    f"See config-help for help on configuration. Existing properties types are: {list(self.__properties_builders.keys())}",
                )

            for p in self.__config.get_properties_write_preprocess_sequence():
                if p not in self.__properties_builders.keys():
                    errors.log_and_throw(
                        to_be_fixed_by=ResolvableBy.CONFIG_ERROR,
                        log=log,
                        what_happened=f"A non-valid properties type {p} configured in "
                        "PROPERTIES_WRITE_PREPROCESS_SEQUENCE.",
                        why_it_happened=f"No IPropertiesServiceClient handler for property type {p} "
                        "was registered in IPropertiesRegistry.",
                        consequences="The write pre-processing failed.",
                        countermeasures=f"Either remove the non-valid properties type {p} from "
                        "PROPERTIES_WRITE_PREPROCESS_SEQUENCE configuration, or"
                        "register a corresponding IPropertiesServiceClient "
                        "implementation via set_properties_factory_method API.",
                    )

            service_properties = DataJobsServiceProperties(
                job_name=self.__job_name,
                team_name=self.__team_name,
                properties_service_client=factory_method(),
                write_preprocessors=[
                    self.__properties_builders.get(p)()
                    for p in self.__config.get_properties_write_preprocess_sequence()
                ],
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
