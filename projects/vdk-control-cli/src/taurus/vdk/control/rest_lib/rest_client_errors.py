# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import functools
import json

from taurus.vdk.control.exception.vdk_exception import VDKException
from taurus_datajob_api import ApiException
from urllib3.exceptions import HTTPError


class ApiClientErrorDecorator:
    def __init__(self, what="Control Service Error"):
        self.what = what

    def _get_error(self, exception: ApiException):
        # noinspection PyBroadException
        try:
            return json.loads(exception.body)
        except:
            error = {}
            if exception.status == 401:
                error = dict(
                    what=self.what,
                    why="The request has not been applied because it lacks valid authentication credentials.",
                    consequences="Operation cannot complete.",
                    countermeasures="Try to login again using VDK CLI login command. "
                    "Make sure you have permission to execute the given operation.",
                )
            if exception.status == 404:
                error = dict(
                    what=self.what,
                    why="The requested resource cannot be found. "
                    "You may have a spelling mistake or the data job has not been created",
                    consequences="Operation cannot complete.",
                    countermeasures="Make sure that the data job name and team name  are spelled correctly (it is is case-sensitive) . "
                    "Make sure you have run  vdkcli create  before doing any other operations on a data job.",
                )

            return error

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            try:
                result = fn(*args, **kwargs)
                return result
            except ApiException as ex:
                body = self._get_error(ex)
                vdk_ex = VDKException(
                    what=body.get("what", self.what),
                    why=body.get("why", f"Http error: status: {ex.status} - {ex.body}"),
                    consequence=body.get(
                        "consequences", "Operation cannot complete successfully."
                    ),
                    countermeasure=body.get(
                        "countermeasures",
                        "See error and try to resolve it or open ticket to SRE team.",
                    ),
                )
                raise vdk_ex from ex
            except HTTPError as ex:
                vdk_ex = VDKException(
                    what=self.what,
                    why=str(ex),
                    consequence="Operation cannot complete successfully.",
                    countermeasure="Verify that the provided url (--rest-api-url) is valid "
                    "and points to the correct host.",
                )
                raise vdk_ex from ex

        return decorated
