# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
errors -- Exception handling implementations

errors is a module that handles all errors.
It defines classes and methods for handling exceptions, and ensuring that there are two types of exceptions:
 - infrastructure-related: should be handled by Platform team.
 - user code-related: should be handled by the owner of the DataJob.
"""
from __future__ import annotations

import enum
import logging
import re
from collections import defaultdict
from enum import Enum

log = logging.getLogger(__name__)

ATTR_VDK_RESOLVABLE_BY = "_vdk_resolvable_by"
ATTR_VDK_RESOLVABLE_ACTUAL = "_vdk_resolvable_actual"

# RESOLVABLE CONTEXT


@enum.unique
class ResolvableBy(str, Enum):
    """
    Type of errors being thrown by VDK during execution of some command.

    Those are:

    * PLATFORM_ERROR - infrastructure errors
    * USER_ERROR - errors in user code/configuration
    * CONFIG_ERROR - errors in the configuration provided to VDK
    """

    PLATFORM_ERROR = "Platform error"
    USER_ERROR = "User Error"
    CONFIG_ERROR = "Configuration error"


@enum.unique
class ResolvableByActual(str, Enum):
    """
    Who is responsible for resolving/fixing the error.

    Each Resolvable error type, along with the corresponding accountable:

    * PLATFORM_ERROR - should be fixed by the PLATFORM (SRE Team, Platform team, operating the infrastructure and services).
    * USER_ERROR - should be fixed by the end USER (or data job owner), for example: supplied bad arguments, bug in user code.
    * CONFIG_ERROR that occurred during:
      - platform run (in case the data job runs on platfrom infrastructure), is handled by the PLATFORM;
      - local run (in case the data job runs on local end user infrastructure), is handled by the USER.

    Returns:
    * PLATFORM - accountable for infrastructure errors, or configuration errors occurred during a platform run;
    * USER - accountable for errors in user code/configuration, or configuration errors occurred during a local run.
    """

    PLATFORM = "Platform"
    USER = "User"


class Resolvable:
    """
    Contains context of a resolvable error
     resolvable_by: Indicates the resolvable type.
     resolvable_by_actual: Who is actually responsible for resolving it
     error_message: the error message
     exception: the exception related to the error
     resolved: indicate if the error is resolved (for example error may be handled in user code and they are considred resolved).
                It should be use for informative purposes. It may be None/empty (for example if error originates from a new thread spawned by a job step)
    """

    def __init__(
        self,
        resolvable_by: ResolvableBy,
        resolvable_by_actual: ResolvableByActual,
        error_message: str,
        exception: BaseException,
        resolved: bool = False,
    ):
        self.resolvable_by = resolvable_by
        self.resolvable_by_actual = resolvable_by_actual
        self.error_message = error_message
        self.exception = exception
        self.resolved = resolved


class ResolvableContext:
    """
    A global registry for resolvable entries lookup, available immediately upon class loading.
    Purposed for keeping track of any errors that may occur before, during or after CoreContext/JobContext initialization.
    """

    # The key is 'blamee' (i.e. responsible for the error fixing) and the value is a list of corresponding Resolvables
    resolvables: dict[ResolvableByActual, list[Resolvable]]
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance

    @classmethod
    def instance(cls):
        return cls.__new__(cls)

    def __init__(self):
        self.resolvables = defaultdict(list)

    def add(self, resolvable: Resolvable) -> None:
        """
        Register a resolvable entry in the context.
        """
        resolvable_by_actual = resolvable.resolvable_by_actual
        if resolvable_by_actual not in self.resolvables.keys():
            self.resolvables[resolvable_by_actual] = []
        self.resolvables[resolvable_by_actual].append(resolvable)

    def clear(self) -> None:
        """
        Clear so far recorded records - those are considered intermediate and resolved.
        For example after successful completion of a step.
        """
        self.resolvables.clear()

    def mark_all_resolved(self):
        for resolvable_by_actual in self.resolvables.values():
            for resolvable in resolvable_by_actual:
                resolvable.resolved = True


def resolvable_context():
    return ResolvableContext.instance()


def clear_intermediate_errors():
    # kept for backwards compatible reasons.
    resolvable_context().clear()


def set_exception_resolvable_by(exception: BaseException, resolvable_by: ResolvableBy):
    setattr(exception, ATTR_VDK_RESOLVABLE_BY, resolvable_by)
    setattr(
        exception,
        ATTR_VDK_RESOLVABLE_ACTUAL,
        __error_type_to_actual_resolver(resolvable_by),
    )


def get_exception_resolvable_by(exception: BaseException):
    if hasattr(exception, ATTR_VDK_RESOLVABLE_BY):
        return getattr(exception, ATTR_VDK_RESOLVABLE_BY)
    else:
        return None


def get_exception_resolvable_by_actual(exception: BaseException):
    resolvable_by = get_exception_resolvable_by(exception)
    if resolvable_by:
        return __error_type_to_actual_resolver(resolvable_by)
    else:
        return None


# ERROR CLASSIFICATION


def get_blamee_overall() -> ResolvableByActual | None:
    """
    Finds who is responsible for fixing the error/s.

    Returns:

    None - if there were no errors
    ResolvableByActual.PLATFORM - if during the run there were only Platfrom exceptions
    ResolvableByActual.USER - if during the run there was at least one job owner exceptions

    The reason it is set to ResolvableByActual.USER if there is at least one job owner is:
    VDK defaults the error to be resolved by Platform team  until it can determine for certain that it's an issue in the job code.
    There might be multiple components logging error (for example in exception propagation), and if at least one component says error is in the job code,
    then we set to be resolved by data job owner.

    """
    if len(resolvable_context().resolvables) == 0:
        return None

    def filter(resolvable_by_actual):
        filtered = [
            i
            for i in resolvable_context().resolvables.get(resolvable_by_actual)
            if not i.resolved
        ]
        return resolvable_by_actual if filtered else None

    if ResolvableByActual.USER in resolvable_context().resolvables:
        return filter(ResolvableByActual.USER)

    if ResolvableByActual.PLATFORM in resolvable_context().resolvables:
        return filter(ResolvableByActual.PLATFORM)


def get_blamee_overall_user_error() -> str:
    """
    Finds the first encountered error where the blamee overall is the owner.

    :return:
       Empty string if the owner is not the overall blamee
       An ErrorMessage instance to string
    """
    blamee = get_blamee_overall()
    if blamee is None or blamee != ResolvableByActual.USER:
        return ""
    blamee_user_errors = resolvable_context().resolvables.get(
        ResolvableByActual.USER, []
    )
    return str(blamee_user_errors[0].exception) if blamee_user_errors else None


def find_whom_to_blame_from_exception(exception: Exception) -> ResolvableBy:
    """
    Tries to determine if it's user or platform error
    """
    if get_exception_resolvable_by(exception):
        return get_exception_resolvable_by(exception)
    return ResolvableBy.PLATFORM_ERROR


def _get_exception_message(exception: Exception) -> str:
    """Returns the message part of an exception as string"""
    return str(exception).strip()


def exception_matches(
    e: Exception, classname_with_package: str, exception_message_matcher_regex: str
) -> bool:
    """
    Tries to see if exception matches given regex expression. Use to detect what type of error is.

    :param e: BaseException: exception whose class and message are to be checked
    :param classname_with_package: full class name, e.g. 'impala.error.HiveServer2Error'
    :param exception_message_matcher_regex: A regex expression that is run against exception message.
    """
    typeMatcher = re.compile(classname_with_package)
    msgMatcher = re.compile(pattern=exception_message_matcher_regex, flags=re.DOTALL)
    t = type(e)  # "<class 'impala.error.HiveServer2Error'>"
    classname = str(t).split("'")[1]
    match = typeMatcher.match(classname)
    if None is match:
        return False
    grp = match.group()
    if not (grp == classname):
        return False

    msg = _get_exception_message(e)
    match = msgMatcher.match(msg)
    if None is match:
        return False
    grp = match.group()
    return grp == msg


def __error_type_to_actual_resolver(to_be_fixed_by: ResolvableBy) -> ResolvableByActual:
    if ResolvableBy.PLATFORM_ERROR == to_be_fixed_by:
        return ResolvableByActual.PLATFORM
    if ResolvableBy.USER_ERROR == to_be_fixed_by:
        return ResolvableByActual.USER
    if ResolvableBy.CONFIG_ERROR == to_be_fixed_by:
        return CONFIGURATION_ERRORS_ARE_TO_BE_RESOLVED_BY
    # We should never reach this
    raise Exception(
        "BUG! Fix me!"
    )  # What type is the error that caused this and whom to blame, Platform or Data Jobs Developer?


# CONVENIENCE

# overwrite when running in kubernetes
CONFIGURATION_ERRORS_ARE_TO_BE_RESOLVED_BY = ResolvableByActual.PLATFORM

MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE = (
    "I'm rethrowing this exception to my caller to process."
    "Most likely this will result in failure of current Data Job."
)
MSG_CONSEQUENCE_TERMINATING_APP = (
    "The provided Data Job will not be executed. Terminating application."
)
MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION = (
    "See contents of the exception and fix the problem that causes it."
)


def MSG_WHY_FROM_EXCEPTION(exception: Exception) -> str:
    """
    Try to figure what is the reason for the failure (why) from the exception and return as a reason.
    """
    if exception_matches(exception, "OSError", ".*File too large.*"):
        message = (
            "File size limit  for Data Job has been exceeded."
            "Optimize the disk utilization of your Data Job."
            "For local runs this limit can be changed by 'export VDK_RESOURCE_LIMIT_DISK_MB=<new-value>'."
            "For cloud run you can fill in a Service Request (http://go/resource-limits) for the limit to be changed."
            "This limit does not apply to macOS and Windows execution environments."
        )
        return f"An exception occurred, exception message was: {message}"

    if exception_matches(exception, "RuntimeError", ".*can't start new thread.*"):
        message = "Unable to start new thread. Optimize thread usage of your Data Job."
        return f"An exception occurred, exception message was: {message}"

    return _get_exception_message(exception)
