# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from copy import deepcopy
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from vdk.api.job_input import ISecrets
from vdk.api.plugin.plugin_input import ISecretsServiceClient

from ...core.errors import log_and_throw
from ...core.errors import ResolvableBy
from .base_secrets_impl import check_valid_secret

log = logging.getLogger(__name__)

SecretValue = Union[int, float, str, list, dict, None]


class DataJobsServiceSecrets(ISecrets):
    """
    Data Jobs Secrets implementation.
    """

    __VALID_TYPES = [int, float, str, list, dict, type(None)]

    def __init__(
        self,
        job_name: str,
        team_name: str,
        secrets_service_client: ISecretsServiceClient,
        write_preprocessors: Optional[List[ISecretsServiceClient]] = None,
    ):
        log.debug(
            f"Data Job Secrets for job {job_name} with service client: {secrets_service_client}"
        )
        self._job_name = job_name
        self._team_name = team_name
        self._secrets_service_client = secrets_service_client
        self._write_preprocessors = write_preprocessors

    def get_secret(self, name: str, default_value: SecretValue = None) -> SecretValue:
        """
        :param name: The name of the secret
        :param default_value: default value ot return if missing
        """
        secrets = self.get_all_secrets()
        if name in secrets:
            return secrets[name]
        else:
            log.warning(
                "Secret {} is not among Job secrets, returning default value: {}".format(
                    name, default_value
                )
            )
            return default_value

    def get_all_secrets(self) -> Dict[str, SecretValue]:
        """
        :return: all stored secrets
        """
        return self._secrets_service_client.read_secrets(
            self._job_name, self._team_name
        )

    def set_all_secrets(self, secrets: Dict[str, SecretValue]) -> None:
        """
        Invokes the write pre-processors if any are configured.
        Persists the passed secrets overwriting all previous properties.
        """
        if self._write_preprocessors:
            secrets = deepcopy(
                secrets
            )  # keeps the outer scope originally-referenced dictionary intact
            for client in self._write_preprocessors:
                try:
                    secrets = client.write_secrets(
                        self._job_name, self._team_name, secrets
                    )
                except Exception as e:
                    log_and_throw(
                        to_be_fixed_by=ResolvableBy.USER_ERROR,
                        log=log,
                        what_happened=f"A write pre-processor of secrets client {client} had failed.",
                        why_it_happened=f"User Error occurred. Exception was: {e}",
                        consequences="SECRETS_WRITE_PREPROCESS_SEQUENCE was interrupted, and "
                        "secrets won't be written by the SECRETS_DEFAULT_TYPE client.",
                        countermeasures="Handle the exception raised.",
                    )

        for k, v in list(secrets.items()):
            check_valid_secret(k, v, DataJobsServiceSecrets.__VALID_TYPES)  # throws

        self._secrets_service_client.write_secrets(
            self._job_name, self._team_name, secrets
        )
