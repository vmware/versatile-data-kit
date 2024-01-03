# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.util.utils import parse_config_sequence

SECRETS_DEFAULT_TYPE = "SECRETS_DEFAULT_TYPE"
SECRETS_WRITE_PREPROCESS_SEQUENCE = "SECRETS_WRITE_PREPROCESS_SEQUENCE"


class SecretsConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def get_secrets_default_type(self) -> str:
        return self.__config.get_value(SECRETS_DEFAULT_TYPE)

    def get_secrets_write_preprocess_sequence(self) -> List[str]:
        return parse_config_sequence(
            self.__config, key=SECRETS_WRITE_PREPROCESS_SEQUENCE, sep=","
        )


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=SECRETS_DEFAULT_TYPE,
        default_value=None,
        description="Set the default secrets type to use. "
        "Plugins can register different secret types. "
        "This option controls which is in use"
        "It can be left empty, in which case "
        "if there is only one type registered it will use it."
        "Or it will use one register with type 'default' ",
    )
    config_builder.add(
        key=SECRETS_WRITE_PREPROCESS_SEQUENCE,
        default_value=None,
        description="""A string of comma-separated secret types.
            Those types are priorly registered in the ISecretsRegistry, by
            mapping a factory for instantiating each ISecretsServiceClient
            secrets type handler.
            This comma-separated string value indicates the sequence in which those
            ISecretsServiceClient implementations `write_secrets` method
            will be invoked. For example:
                   SECRETS_WRITE_PREPROCESS_SEQUENCE="a-prefixed-secret,
                   replicated-secret"
            would mean that the secrets data stored would be first
            processed by the `a-prefixed-secret` client, then by the
            `replicated-secret` client, and finally would be stored by
            the default secret client.
            In case of pre-processing failure, the default client won't be invoked.
            """,
    )
