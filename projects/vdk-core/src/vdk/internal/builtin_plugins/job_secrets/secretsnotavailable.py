# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Callable

from vdk.api.job_input import ISecrets


class SecretsNotAvailable(ISecrets):
    """
    Implementation of IProperties that will throw an error if user tries to access them.
    """

    def __init__(self, error_handler: Callable[[str], None]):
        self._error_handler = error_handler

    def get_secret(self, name, default_value=None):  # @UnusedVariable
        self.tell_user("get_secret")

    def get_all_secrets(self):  # @UnusedVariable
        self.tell_user("get_all_secrets")

    def set_all_secrets(self, properties):  # @UnusedVariable
        self.tell_user("set_all_secrets")

    def tell_user(self, methodname: str) -> None:
        self._error_handler(methodname)
