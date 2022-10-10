# Copyright 2021 VMware, Inc.
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
import sys
import traceback
from collections import defaultdict
from enum import Enum
from logging import Logger
from types import TracebackType
from typing import cast

log = logging.getLogger(__name__)
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


# overwrite when running in kubernetes
CONFIGURATION_ERRORS_ARE_TO_BE_RESOLVED_BY = ResolvableByActual.PLATFORM


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
        error_message: ErrorMessage,
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


class BaseVdkError(Exception):
    """For all errors risen from our "code" (vdk)

    There are two child branches in exception hierarchy:
     - Service errors
     - Domain errors
    """

    def __init__(self, error_message: ErrorMessage):
        """

        :param error_message: required - error message describing the error
        :param cause_exception: cause exception. Included if you want to be visualized by toString().
                In python you specify cause using `raise X from Cause`
                https://docs.python.org/3/tutorial/errors.html#exception-chaining
        """
        super().__init__(str(error_message))


class PlatformServiceError(BaseVdkError):
    """
    Error caused by issue in Platform

    Service error are those errors which indicate for bad condition of the service. which prevent the normal
    completion of given request. User can do little more beyond retrying.
    """

    pass


class DomainError(BaseVdkError):
    """
    Domain errors are always function of the input and the current system state.

    In contrast to the service errors they occur always upon same conditions.
    In most of the cases the client can determine what is wrong and knows how to recover.
    """

    pass


class VdkConfigurationError(DomainError):
    """
    An exception in the configuration of the Data Job

    If job is executed on user (local execution) premises - this is considered #RESOLVED_BY_JOB_OWNER
    Otherwise If job is executed in "cloud" - this is considered #RESOLVED_BY_PLATFORM class of error
    """

    pass


class UserCodeError(DomainError):
    """Exception in user code"""

    pass


class SkipRemainingStepsException(DomainError):
    """
    An exception used to skip the remaining steps of a Data Job.

    When this exception is thrown from a data job python step, all the other steps will
    be skipped and the data job execution will exit and be marked as success.
    """

    pass


class ErrorMessage:
    """
    Standard format for Error messages in VDK. Use it when throwing exceptions or logging error level.
    """

    def __init__(
        self, summary: str, what: str, why: str, consequences: str, countermeasures: str
    ):
        self.summary = summary
        self.what = what
        self.why = why
        self.consequences = consequences
        self.countermeasures = countermeasures

    def _get_template(self, replace_with: str) -> str:
        return "{}r%15s : {}r%15s : {}r%15s : {}r%15s : {}".replace(
            "r", replace_with
        ) % (
            "what happened".upper(),
            "why it happened".upper(),
            "consequences".upper(),
            "countermeasures".upper(),
        )

    def _to_string(self, template: str) -> str:
        return template.format(
            self.summary, self.what, self.why, self.consequences, self.countermeasures
        )

    def __str__(self) -> str:
        return self._to_string(self._get_template("\n"))

    def to_html(self) -> str:
        """
        :return: html representaiton of the error.
        """
        return self._to_string(self._get_template("<br />"))


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
    return str(blamee_user_errors[0].error_message) if blamee_user_errors else None


def log_exception(
    to_be_fixed_by: ResolvableBy,
    log: Logger,
    what_happened: str,
    why_it_happened: str,
    consequences: str,
    countermeasures: str,
    exception: BaseException,
) -> None:
    """
    Log message only if it has not been logged already.
    Does not throw it again.
    """
    if __error_is_logged(exception):
        return

    resolvable_by_actual = __error_type_to_actual_resolver(to_be_fixed_by)
    error_message = __build_message_for_end_user(
        to_be_fixed_by,
        resolvable_by_actual,
        what_happened,
        why_it_happened,
        consequences,
        countermeasures,
    )
    resolvable_context().add(
        Resolvable(to_be_fixed_by, resolvable_by_actual, error_message, exception)
    )

    __set_error_is_logged(exception)
    log.exception(error_message)


def log_and_throw(
    to_be_fixed_by: ResolvableBy,
    log: Logger,
    what_happened: str,
    why_it_happened: str,
    consequences: str,
    countermeasures: str,
) -> None:
    """
    Log error message and then throw it to be handled up the stack.
    """

    resolvable_by_actual = __error_type_to_actual_resolver(to_be_fixed_by)
    error_message = __build_message_for_end_user(
        to_be_fixed_by,
        resolvable_by_actual,
        what_happened,
        why_it_happened,
        consequences,
        countermeasures,
    )

    exception: BaseVdkError
    if ResolvableBy.PLATFORM_ERROR == to_be_fixed_by:
        exception = PlatformServiceError(error_message)
    elif ResolvableBy.USER_ERROR == to_be_fixed_by:
        exception = UserCodeError(error_message)
    elif ResolvableBy.CONFIG_ERROR == to_be_fixed_by:
        exception = VdkConfigurationError(error_message)
    else:
        raise Exception(
            "BUG! Fix me!"
        )  # What type is the error that caused this and whom to blame Platform or Data Jobs Developer?

    try:
        raise exception
    except BaseVdkError as e:
        resolvable_context().add(
            Resolvable(to_be_fixed_by, resolvable_by_actual, error_message, e)
        )
        lines = __get_caller_stacktrace()
        log.error(str(error_message) + "\n" + lines)
        __set_error_is_logged(e)
        raise


def log_and_rethrow(
    to_be_fixed_by: ResolvableBy,
    log: Logger,
    what_happened: str,
    why_it_happened: str,
    consequences: str,
    countermeasures: str,
    exception: BaseException,
    wrap_in_vdk_error=False,
) -> None:
    """
    Log message only if it has not been logged already. And throws it again. Use it to handle coming exceptions.
    :param to_be_fixed_by:
    :param log:
    :param what_happened: same as ErrorMessage#what
    :param why_it_happened: same as ErrorMessage#why
    :param consequences: same as ErrorMessage#consequences
    :param countermeasures: same as ErrorMessage#countermeasures
    :param exception: the exception message to re-throw
    :param wrap_in_vdk_error: If the exception is not wrapped by BaseVdkError
            it will wrap it in corresponding BaseVdkError exception based on to_be_fixed_by parameter
    """

    resolvable_by_actual = __error_type_to_actual_resolver(to_be_fixed_by)
    error_message = __build_message_for_end_user(
        to_be_fixed_by,
        resolvable_by_actual,
        what_happened,
        why_it_happened,
        consequences,
        countermeasures,
    )

    to_be_raised_exception = exception
    if wrap_in_vdk_error:
        to_be_raised_exception = __wrap_exception_if_not_already(
            to_be_fixed_by, error_message, exception
        )

    if not __error_is_logged(exception):
        log.exception(error_message)
        __set_error_is_logged(exception)

    try:
        raise to_be_raised_exception from exception if wrap_in_vdk_error else exception
    except Exception as e:
        resolvable_context().add(
            Resolvable(to_be_fixed_by, resolvable_by_actual, error_message, e)
        )
        raise


def find_whom_to_blame_from_exception(exception: Exception) -> ResolvableBy:
    """
    Tries to determine if it's user or platform error
    """
    if issubclass(type(exception), UserCodeError):
        return ResolvableBy.USER_ERROR
    if issubclass(type(exception), VdkConfigurationError):
        return (
            ResolvableBy.CONFIG_ERROR
        )  # TODO find out if this is a local or platform deployment and fix this line.
    if issubclass(type(exception), PlatformServiceError):
        return ResolvableBy.PLATFORM_ERROR
    return ResolvableBy.PLATFORM_ERROR


def _get_exception_message(exception: Exception) -> str:
    """Returns the message part of an exception as string"""
    return str(exception).strip()


class __CustomMessageExceptionDecorator:
    """
    Provides custom message for an exception.

    Needed in order for the end-user to be better informed for the exceptional condition.
    """

    def __init__(self, exception: Exception) -> None:
        self._exception = exception

    def get_custom_message(self) -> str | None:
        """
        Attach custom message for end-user to exception.

        :return: decorated exception message.
        """
        return self._decorate_exception_message(self._exception)

    @staticmethod
    def _decorate_exception_message(exception: Exception) -> str | None:
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
            message = (
                "Unable to start new thread. Optimize thread usage of your Data Job."
            )
            return f"An exception occurred, exception message was: {message}"
        return None


def MSG_WHY_FROM_EXCEPTION(exception: Exception) -> str:
    """
    Try to figure what is the reason for the failure (why) from the exception and return as a reason.
    """
    custom_message = __CustomMessageExceptionDecorator(exception).get_custom_message()
    return (
        custom_message
        if custom_message
        else "An exception occurred, exception message was: {}".format(
            _get_exception_message(exception)
        )
    )


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


def __build_message_for_end_user(
    to_be_fixed_by: ResolvableBy,
    to_be_fixed_by_actual: ResolvableByActual,
    what_happened: str,
    why_it_happened: str,
    consequences: str,
    countermeasures: str,
) -> ErrorMessage:
    error = ""
    if ResolvableBy.PLATFORM_ERROR == to_be_fixed_by:
        error = " Platform service error "
    elif ResolvableBy.USER_ERROR == to_be_fixed_by:
        error = "n error in data job code "
    elif ResolvableBy.CONFIG_ERROR == to_be_fixed_by:
        error = " configuration error "

    return ErrorMessage(
        "A{} occurred. The error should be resolved by {}. Here are the details:".format(
            error, to_be_fixed_by_actual
        ),
        what_happened.strip(),
        why_it_happened.strip(),
        consequences.strip(),
        countermeasures.strip(),
    )


def __get_caller_stacktrace(exception: BaseException = None) -> str:
    """
    :return: stacktrace excluding this method (hence caller stacktrace)
    """
    tb = (
        exception.__traceback__
        if exception and exception.__traceback__
        else cast(TracebackType, sys.exc_info()[2])
    )
    f = tb.tb_frame.f_back
    lst = ["Traceback (most recent call first):\n"]
    fstack = traceback.extract_stack(f)
    fstack.reverse()
    lst = lst + traceback.format_list(fstack)
    lines = ""
    for line in lst:
        lines = lines + line
    return lines


def __error_type_to_actual_resolver(to_be_fixed_by: ResolvableBy) -> ResolvableByActual:
    if ResolvableBy.PLATFORM_ERROR == to_be_fixed_by:
        return ResolvableByActual.PLATFORM
    if ResolvableBy.USER_ERROR == to_be_fixed_by:
        return ResolvableByActual.USER
    if ResolvableBy.CONFIG_ERROR == to_be_fixed_by:
        return CONFIGURATION_ERRORS_ARE_TO_BE_RESOLVED_BY
    raise Exception(
        "BUG! Fix me!"
    )  # What type is the error that caused this and whom to blame, Platform or Data Jobs Developer?


def __wrap_exception_if_not_already(
    to_be_fixed_by: ResolvableBy, msg: ErrorMessage, exception: BaseException
):
    if isinstance(exception, BaseVdkError):
        # already wrapped
        return exception

    # TODO: how to assign cause (new_ex from old_ex) ?
    if ResolvableBy.PLATFORM_ERROR == to_be_fixed_by:
        return PlatformServiceError(msg)
    elif ResolvableBy.USER_ERROR == to_be_fixed_by:
        return UserCodeError(msg)
    elif ResolvableBy.CONFIG_ERROR == to_be_fixed_by:
        return VdkConfigurationError(msg)
    else:
        log.warning(
            "Unknown to_be_fixed_by type. "
            "This seems like a bug. We cannot wrap exception and return original one "
        )
        return exception


def __error_is_logged(exception: BaseException) -> bool:
    """Check if exception has custom added attribute is_logged"""
    return hasattr(exception, "is_logged")


def __set_error_is_logged(exception: BaseException):
    setattr(exception, "is_logged", True)
