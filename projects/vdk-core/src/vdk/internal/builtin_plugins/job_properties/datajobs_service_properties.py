# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from copy import deepcopy
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from vdk.api.job_input import IProperties
from vdk.api.plugin.plugin_input import IPropertiesServiceClient

from ...core.errors import log_and_throw
from ...core.errors import ResolvableBy
from .base_properties_impl import check_valid_property

log = logging.getLogger(__name__)

PropertyValue = Union[int, float, str, list, dict, None]


class DataJobsServiceProperties(IProperties):
    """
    Data Jobs Properties implementation.
    """

    __VALID_TYPES = [int, float, str, list, dict, type(None)]

    def __init__(
        self,
        job_name: str,
        team_name: str,
        properties_service_client: IPropertiesServiceClient,
        write_preprocessors: Optional[List[IPropertiesServiceClient]] = None,
    ):
        log.debug(
            f"Data Job Properties for job {job_name} with service client: {properties_service_client}"
        )
        self._job_name = job_name
        self._team_name = team_name
        self._properties_service_client = properties_service_client
        self._write_preprocessors = write_preprocessors

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
        return self._properties_service_client.read_properties(
            self._job_name, self._team_name
        )

    def set_all_properties(self, properties: Dict[str, PropertyValue]) -> None:
        """
        Invokes the write pre-processors if any such configured.
        Persists the passed properties overwriting all previous properties.
        """
        if self._write_preprocessors:
            properties = deepcopy(
                properties
            )  # keeps the outer scope originally-referenced dictionary intact
            for client in self._write_preprocessors:
                try:
                    properties = client.write_properties(
                        self._job_name, self._team_name, properties
                    )
                except Exception as e:
                    log_and_throw(
                        to_be_fixed_by=ResolvableBy.USER_ERROR,
                        log=log,
                        what_happened=f"A write pre-processor of properties client {client} had failed.",
                        why_it_happened=f"User Error occurred. Exception was: {e}",
                        consequences="PROPERTIES_WRITE_PREPROCESS_SEQUENCE was interrupted, and "
                        "properties won't be written by the PROPERTIES_DEFAULT_TYPE client.",
                        countermeasures=f"Handle the exception raised.",
                    )

        for (k, v) in list(properties.items()):
            check_valid_property(
                k, v, DataJobsServiceProperties.__VALID_TYPES
            )  # throws

        self._properties_service_client.write_properties(
            self._job_name, self._team_name, properties
        )
