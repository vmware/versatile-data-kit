# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict
from typing import Union

from taurus.api.job_input import IProperties
from taurus.api.plugin.plugin_input import IPropertiesServiceClient

from .base_properties_impl import check_valid_property

log = logging.getLogger(__name__)


PropertyValue = Union[int, float, str, list, dict, None]


class DataJobsServiceProperties(IProperties):
    """
    Data Jobs Properties implementation.
    """

    __VALID_TYPES = [int, float, str, list, dict, type(None)]

    def __init__(
        self, job_name: str, properties_service_client: IPropertiesServiceClient
    ):
        log.debug(
            f"Data Job Properties for job {job_name} with service client: {properties_service_client}"
        )
        self._job_name = job_name
        self._properties_service_client = properties_service_client

    def get_property(
        self, name: str, default_value: PropertyValue = None
    ) -> PropertyValue:
        """
        :param name: The name of the property
        :param default_value: default value ot return if missing
        """
        properties = self.get_all_properties()
        if name in properties:
            return properties[name]
        else:
            log.warning(
                "Property {} is not among Job properties, returning default value: {}".format(
                    name, default_value
                )
            )
            return default_value

    def get_all_properties(self) -> Dict[str, PropertyValue]:
        """
        :return: all stored properties
        """
        return self._properties_service_client.read_properties(self._job_name)

    def set_all_properties(self, properties: Dict[str, PropertyValue]) -> None:
        """
        Persists the passed properties overwriting all previous properties
        """
        for (k, v) in list(properties.items()):
            check_valid_property(
                k, v, DataJobsServiceProperties.__VALID_TYPES
            )  # throws

        self._properties_service_client.write_properties(self._job_name, properties)
