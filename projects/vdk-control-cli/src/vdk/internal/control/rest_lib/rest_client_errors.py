# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import functools
import json
import logging

from taurus_datajob_api import ApiException
from urllib3.exceptions import HTTPError
from vdk.internal.control.exception.vdk_exception import VDKException

log = logging.getLogger(__name__)


class ApiClientErrorDecorator:
    def __init__(
        self, what="Control Service Error", consequences="Operation cannot complete."
    ):
        self.__what = what
        self.__consequences = consequences

    def _get_error(self, exception: ApiException):
        try:
            return json.loads(exception.body)
        except:
            error = {}
            if exception.status == 401:
                error = dict(
                    what=self.__what,
                    why=f"The request has not been applied because it lacks valid authentication credentials. "
                    f"Error returned by control service is {exception.body}",
                    consequences=self.__consequences,
                    countermeasures="Try to login again using VDK CLI login command."
                    "Or set correct api token configuration (see vdk config-help)."
                    "Make sure you have permission to execute the given operation."
                    "Investigate (google) the error returned by control service."
                    "And if all fails try to contact the support team.",
                )
            if exception.status == 404:
                error = dict(
                    what=self.__what,
                    why="The requested resource cannot be found. "
                    "You may have a spelling mistake or the data job has not been created",
                    consequences=self.__consequences,
                    countermeasures="Make sure that the data job name and team name are spelled correctly "
                    "(it is case-sensitive) . "
                    "Make sure you have run `vdk create --cloud` before doing this operation on a data job.",
                )

            return error

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            try:
                log.debug(f"Call function {fn.__module__}.{fn.__name__}")
                result = fn(*args, **kwargs)
                return result
            except ApiException as ex:
                log.debug(
                    f"An API Exception occurred in {fn.__module__}.{fn.__name__}",
                    f"The Exception class was: {ex}",
                )

                body = self._get_error(ex)
                vdk_ex = VDKException(
                    what=body.get("what", self.__what),
                    why=body.get("why", f"Http error: status: {ex.status} - {ex.body}"),
                    consequence=body.get("consequences", self.__consequences),
                    countermeasure=body.get(
                        "countermeasures",
                        "See error and try to resolve it or open ticket to SRE team.",
                    ),
                )
                raise vdk_ex from ex
            except HTTPError as ex:
                log.debug(
                    f"An HTTP Exception occurred in {fn.__module__}.{fn.__name__}",
                    f"The Exception class was: {ex}",
                )

                vdk_ex = VDKException(
                    what=self.__what,
                    why=str(ex),
                    consequence=self.__consequences,
                    countermeasure="Verify that the provided url (--rest-api-url) is valid "
                    "and points to the correct host.",
                )
                raise vdk_ex from ex

        return decorated
