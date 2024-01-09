# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any

from vdk.api.job_input import ISecrets
from vdk.api.plugin.plugin_input import ISecretsFactory
from vdk.api.plugin.plugin_input import ISecretsRegistry
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.job_secrets.cached_secrets import (
    CachedSecretsWrapper,
)
from vdk.internal.builtin_plugins.job_secrets.datajobs_service_secrets import (
    DataJobsServiceSecrets,
)
from vdk.internal.builtin_plugins.job_secrets.secrets_config import (
    SecretsConfiguration,
)
from vdk.internal.builtin_plugins.job_secrets.secretsnotavailable import (
    SecretsNotAvailable,
)
from vdk.internal.core import errors
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import ResolvableBy
from vdk.internal.util.decorators import LogDecorator

log: logging.Logger = logging.getLogger(__name__)


class SecretsRouter(ISecretsRegistry, ISecrets):
    """
    Implements registry of ISecrets.
    """

    def __init__(self, job_name: str, cfg: Configuration):
        self.__secrets_builders = {}
        self.__cached_secrets_impl = None
        self.__job_name = job_name
        self.__team_name = cfg.get_value(JobConfigKeys.TEAM.value)
        self.__config = SecretsConfiguration(cfg)

    @LogDecorator(log)
    def set_secrets_factory_method(
        self, secrets_type: str, secrets_factory: ISecretsFactory
    ) -> None:
        self.__secrets_builders[secrets_type] = secrets_factory

    def get_secret(self, name: str, default_value: Any = None) -> str:
        return self.__get_secrets_impl().get_secret(name, default_value)

    def get_all_secrets(self) -> dict:
        return self.__get_secrets_impl().get_all_secrets()

    def set_all_secrets(self, secrets: dict):
        self.__get_secrets_impl().set_all_secrets(secrets)

    def has_secrets_impl(self) -> bool:
        """
        Is any secrets implementation backend available
        :return: bool
        """
        return not isinstance(self.__get_secrets_impl(), SecretsNotAvailable)

    def __get_secrets_impl(self):
        """
        Singleton secrets backend implementation.
        """
        if not self.__cached_secrets_impl:
            if self.__secrets_builders:
                self.__cached_secrets_impl = self.__setup_secrets_from_factory_method()
            else:
                why = "No secrets client implementation has been installed or configured. "
                countermeasures = (
                    "Check if you have installed properly vdk. "
                    "Check if you need to install some plugin for secrets. "
                    "If a plugin is installed, check out plugin documentation"
                    " whether the plugin is configured correctly."
                )
                error_handler = self.__secrets_not_available_error_handler(
                    why=why, countermeasures=countermeasures
                )
                self.__cached_secrets_impl = SecretsNotAvailable(error_handler)
        return self.__cached_secrets_impl

    def __choose_from_default_type(self, secrets_type: str):
        if secrets_type in self.__secrets_builders:
            return self.__secrets_builders.get(secrets_type)
        else:
            errors.report_and_throw(
                errors.VdkConfigurationError(
                    f"secrets default type was configured to be {secrets_type} "
                    "no such secrets api implementation has been registered",
                    "Check if the job has not been mis-configured - for example misspelling error. "
                    f"See config-help for help on configuration. Existing secrets types are: {list(self.__secrets_builders.keys())} "
                    "Alternatively make sure the correct plugin has been installed "
                    "providing the secrets api implementation ",
                )
            )

    def __setup_secrets_from_factory_method(self):
        try:
            secrets_type = self.__config.get_secrets_default_type()
            factory_method = None
            if secrets_type:
                factory_method = self.__choose_from_default_type(secrets_type)
            elif "default" in self.__secrets_builders:
                factory_method = self.__choose_from_default_type("default")
            elif len(self.__secrets_builders) == 1:
                factory_method = self.__secrets_builders[
                    list(self.__secrets_builders.keys())[0]
                ]
            else:
                errors.report_and_throw(
                    errors.VdkConfigurationError(
                        "Secrets API client cannot be chosen.",  # set by handler
                        "Too many choices for secrets client implementation.",
                        "Secrets API functionality does not work.",  # set by handler
                        "Configure which secrets client implementation "
                        "to use with secrets_default_type config option. "
                        f"See config-help for help on configuration. Existing secret types are: {list(self.__secrets_builders.keys())}",
                    )
                )

            for p in self.__config.get_secrets_write_preprocess_sequence():
                if p not in self.__secrets_builders:
                    errors.report_and_throw(
                        errors.VdkConfigurationError(
                            f"A non-valid secrets type {p} configured in "
                            "SECRETS_WRITE_PREPROCESS_SEQUENCE.",
                            f"No ISecretsServiceClient handler for secret type {p} "
                            "was registered in ISecretsRegistry.",
                            "The write pre-processing failed.",
                            f"Either remove the non-valid secret type {p} from "
                            "SECRETS_WRITE_PREPROCESS_SEQUENCE configuration, or"
                            "register a corresponding ISecretsServiceClient "
                            "implementation via set_secrets_factory_method API.",
                        )
                    )
            service_secrets = DataJobsServiceSecrets(
                job_name=self.__job_name,
                team_name=self.__team_name,
                secrets_service_client=factory_method(),
                write_preprocessors=[
                    self.__secrets_builders.get(p)()
                    for p in self.__config.get_secrets_write_preprocess_sequence()
                ],
            )
            return CachedSecretsWrapper(service_secrets)
        except Exception as e:
            log.warning(
                "Could not build secrets provider. "
                "This will result in failure if getting/setting secrets is used."
            )
            error_handler = self.__secrets_not_available_error_handler(str(e))
            return SecretsNotAvailable(error_handler)

    @staticmethod
    def __secrets_not_available_error_handler(why, countermeasures=None):
        if not countermeasures:
            countermeasures = " Check why it happened and try to resolve the issue or open a ticket to SRE team."

        def error_handler(methodname):
            return errors.report_and_throw(
                errors.VdkConfigurationError(
                    f"I'm trying to call method '{methodname}' and failed.",
                    why,
                    "Current  Step will fail, and as a result the whole Data Job will fail.",
                    countermeasures,
                )
            )

        return error_handler
