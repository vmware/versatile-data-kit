# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from abc import ABC
from abc import abstractmethod
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from requests.adapters import Retry
from requests.auth import AuthBase
from taurus.api.plugin.plugin_input import IPropertiesServiceClient
from taurus.vdk.core import errors

log = logging.getLogger(__name__)


class Authenticator(ABC):
    @abstractmethod
    def authenticate(self) -> Optional[AuthBase]:
        """Authenticate users and return AuthBase necessary for http requests.
        If authentication is disabled then it will return None
        """
        pass

    @abstractmethod
    def get_authentication_instructions(self) -> str:
        """
        Specifies message with how end user need to authenticate
        """
        pass


class NoneAuthenticator(Authenticator):
    def authenticate(self) -> Optional[AuthBase]:
        return None

    def get_authentication_instructions(self) -> str:
        return "Authentication is disabled. You need to enable it."


class ControlPlanePropertiesServiceClient(IPropertiesServiceClient):
    """
    Implementation of PropertiesClient which connects to Pipelines Control Service Properties API

    The implementation is similar to one in vdk-control-cli.
    It's currently separated because of required support for kerberos which may not be required in vdk-control-cli
    TODO: we should consider dropping this in favor of vdk-control-cli based only. (DRY principle)
    """

    def __init__(
        self,
        url_pattern_with_job_name: str,
        team_name="",
        authenticator: Authenticator = NoneAuthenticator(),
        retries: int = 10,
    ):
        if not (
            "{job_name}" in url_pattern_with_job_name
            and "{team_name}" in url_pattern_with_job_name
        ):
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                log=log,
                what_happened="Properties API URL not valid.",
                why_it_happened="It's expected to have '{team_name}' and '{job_name}' pattern inside",
                consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail. ",
                countermeasures=f"This is likely a bug or misconfiguration. "
                f"Check configuration or contact support team. ",
            )
        self._url = url_pattern_with_job_name
        self._team_name = team_name
        self._authenticator = authenticator
        self._retry_strategy = Retry(
            total=retries,
            read=5,
            connect=5,
            backoff_factor=3,
            raise_on_status=False,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "PUT"],
        )
        log.debug(
            f"Initialized Properties against {self._url} with team {team_name} and authentication {authenticator}"
        )

    def read_properties(self, job_name):
        with self._new_http_session() as session:
            res = session.get(
                self._url.format(team_name=self._team_name, job_name=job_name),
                verify=False,
            )

            self._validate_response(res, "read_properties")  # throws

            return json.loads(res.content.decode("utf-8"))

    def _new_http_session(self):
        session = requests.session()

        adapter = HTTPAdapter(max_retries=self._retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.auth = self._authenticator.authenticate()
        return session

    def write_properties(self, job_name, properties):
        """
        We are adding retries on writing properties
        since we are using PUT to overwrite all properties which is idempotent operation.
        """
        with self._new_http_session() as session:
            res = session.put(
                self._url.format(team_name=self._team_name, job_name=job_name),
                json=properties,
                verify=False,
            )
            self._validate_response(res, "write_properties")  # throws

    def _validate_response(self, response, methodname):
        if response.status_code == 401:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                log=log,
                what_happened="I'm trying to call method '{}' and failed.".format(
                    methodname
                ),
                why_it_happened=f"401 UNAUTHORIZED - {response.text}",
                consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail. ",
                countermeasures=f"Make sure you have authenticated correctly. "
                f"Instructions: {self._authenticator.get_authentication_instructions()}",
            )
        elif response.status_code == 403:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=log,
                what_happened="I'm trying to call method '{}' and failed.".format(
                    methodname
                ),
                why_it_happened=f"403 FORBIDDEN - {response.text}",
                consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail. ",
                countermeasures=f"Check permissions for the user and make sure you have authenticated correctly. "
                f"Instructions: {self._authenticator.get_authentication_instructions()}",
            )
        elif response.status_code >= 500:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.PLATFORM_ERROR,
                log=log,
                what_happened="I'm trying to call method '{}' and failed.".format(
                    methodname
                ),
                why_it_happened=f"{response.status_code} SERVER ERROR - {response.text}",
                consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail. ",
                countermeasures="Please, report this bug to support team.",
            )
