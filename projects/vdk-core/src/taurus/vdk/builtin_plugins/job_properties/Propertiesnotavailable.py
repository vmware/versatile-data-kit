# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Callable

from taurus.api.job_input import IProperties


class PropertiesNotAvailable(IProperties):
    """
    Implementation of IProperties that will throw an error if user tries to access them.
    """

    def __init__(self, error_handler: Callable[[str], None]):
        self._error_handler = error_handler
        pass

    def get_property(self, name, default_value=None):  # @UnusedVariable
        self.tell_user("get_property")

    def get_all_properties(self):  # @UnusedVariable
        self.tell_user("get_all_properties")

    def set_all_properties(self, properties):  # @UnusedVariable
        self.tell_user("set_all_properties")

    def tell_user(self, methodname: str) -> None:
        self._error_handler(methodname)
