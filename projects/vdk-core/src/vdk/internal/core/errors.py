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

import logging
import re
import sys
import traceback
from collections import defaultdict
from enum import Enum
from logging import Logger
from types import TracebackType
from typing import Any
from typing import cast

from click import ClickException


class ResolvableBy(str, Enum):
    """
    Type of errors being thrown by VDK during execution of some command based on who is responsible for resolving/fixing them

    Those are:

    * PLATFORM_ERROR - for infrastructure errors that can and should be fixed by SRE Team, Platform team, operating the infrastructure and services.
    * USER_ERROR - Errors in user code/configuration, that should be fixed by the end user (or job owner) for example: supplied bad arguments, bug in user code.
    * CONFIG_ERROR - Errors in the configuration provided to VDK. Should be fixed by Platform if run in Platfrom infrastructure, or by end user, when run locally.
    """

    PLATFORM_ERROR = "Platform error"
    USER_ERROR = "User Error"
    CONFIG_ERROR = "Configuration error"


# TODO: instead of global variable set this in JobContext
#  (one benefit this way we can run even multiple jobs/templates in the same process)
# The key is 'blamee' (i.e. responsible for the error fixing) and the value is a list of corresponding ErrorMessages
BLAMEES: dict[str, list[Any]] = defaultdict(list)

# overide when running in kubernetes
CONFIGURATION_ERRORS_ARE_TO_BE_RESOLVED_BY = ResolvableBy.PLATFORM_ERROR

log = logging.getLogger(__name__)


class BaseVdkError(ClickException):
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


def get_blamee_overall() -> str | None:
    """
    Finds who is responsible for fixing the error/s.

    Returns:

    None - if there were no errors
    ResolvableBy.PLATFORM_ERROR - if during the run there were only Platfrom exception
    ResolvableBy.USER_ERROR - if during the run there was at least one job owner exceptions

    The reason it is set to ResolvableBy.USER_ERROR if there is at least one job owner is:
    VDK defaults the error to be resolved by Platform team  until it can determine for certain that it's an issue in the job code.
    There might be multiple components logging error (for example in exception propagation), and if at least one component says error is in the job code,
    then we set to be resolved by data job owner.

    """
    if len(BLAMEES) == 0:
        return None
    else:
        return (
            ResolvableBy.USER_ERROR
            if ResolvableBy.USER_ERROR in BLAMEES
            else ResolvableBy.PLATFORM_ERROR
        )


def get_blamee_overall_user_error() -> str:
    """
    Finds the first encountered error where the blamee overall is the owner.

    :return:
       Empty string if the owner is not the overall blamee
       An ErrorMessage instance
    """
    blamee = get_blamee_overall()
    if blamee is None or blamee == ResolvableBy.PLATFORM_ERROR:
        return ""
    blamee_errors = BLAMEES.get(blamee, [])
    return str(blamee_errors[0])


def get_error_type() -> str | None:
    """
    :return: "User" or "Platform"
    """
    blamee = get_blamee_overall()
    return (
        "User" if blamee == ResolvableBy.USER_ERROR else "Platform" if blamee else None
    )


def _build_message_for_end_user(
    to_be_fixed_by: ResolvableBy,
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

    current_error_responsible_for_resolution = _error_type_to_actual_resolver(
        to_be_fixed_by
    )
    # statement to add the key in the dictionary (if not already there),
    # for get_blamee_overall()' to be calculated correctly
    BLAMEES[current_error_responsible_for_resolution]
    responsible_for_resolution = get_blamee_overall()

    msg = ErrorMessage(
        "A{} occurred. The error should be resolved by {}. Here are the details:".format(
            error, responsible_for_resolution
        ),
        what_happened.strip(),
        why_it_happened.strip(),
        consequences.strip(),
        countermeasures.strip(),
    )

    BLAMEES[current_error_responsible_for_resolution].append(msg)
    return msg


def get_caller_stacktrace() -> str:
    """
    :return: stacktrace excluding this method (hence caller stacktrace)
    """
    info = sys.exc_info()
    tb = cast(TracebackType, info[2])
    f = tb.tb_frame.f_back
    lst = ["Traceback (most recent call first):\n"]
    fstack = traceback.extract_stack(f)
    fstack.reverse()
    lst = lst + traceback.format_list(fstack)
    lines = ""
    for line in lst:
        lines = lines + line
    return lines


def _error_type_to_actual_resolver(to_be_fixed_by: ResolvableBy) -> str:
    if ResolvableBy.CONFIG_ERROR == to_be_fixed_by:
        return CONFIGURATION_ERRORS_ARE_TO_BE_RESOLVED_BY
    else:
        return to_be_fixed_by


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
    msg = _build_message_for_end_user(
        to_be_fixed_by, what_happened, why_it_happened, consequences, countermeasures
    )

    try:
        if ResolvableBy.PLATFORM_ERROR == to_be_fixed_by:
            raise PlatformServiceError(msg)
        elif ResolvableBy.USER_ERROR == to_be_fixed_by:
            raise UserCodeError(msg)
        elif ResolvableBy.CONFIG_ERROR == to_be_fixed_by:
            raise VdkConfigurationError(msg)
        else:
            raise Exception(
                "BUG! Fix me!"
            )  # What type is the error that caused this and whom to blame Platform or Data Jobs Developer?
    except BaseVdkError as e:
        lines = get_caller_stacktrace()
        log.error(str(msg) + "\n" + lines)
        __set_error_is_logged(e)
        raise


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
    msg = _build_message_for_end_user(
        to_be_fixed_by, what_happened, why_it_happened, consequences, countermeasures
    )
    __set_error_is_logged(exception)
    log.exception(msg)


def wrap_exception_if_not_already(
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

    msg = _build_message_for_end_user(
        to_be_fixed_by, what_happened, why_it_happened, consequences, countermeasures
    )
    to_be_raised_exception = exception
    if wrap_in_vdk_error:
        to_be_raised_exception = wrap_exception_if_not_already(
            to_be_fixed_by, msg, exception
        )

    if not __error_is_logged(exception):
        log.exception(msg)
        __set_error_is_logged(exception)

    if wrap_in_vdk_error:
        raise to_be_raised_exception from exception
    else:
        raise exception


def __error_is_logged(exception: BaseException) -> bool:
    """Check if exception has custom added attribute is_logged"""
    return hasattr(exception, "is_logged")


def __set_error_is_logged(exception: BaseException):
    setattr(exception, "is_logged", True)


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


def get_exception_message(exception: Exception) -> str:
    """Returns the message part of an exception as string"""
    return str(exception).strip()


class CustomMessageExceptionDecorator:
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
    custom_message = CustomMessageExceptionDecorator(exception).get_custom_message()
    if custom_message:
        return custom_message
    else:
        return "An exception occurred, exception message was: {}".format(
            get_exception_message(exception)
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

    msg = get_exception_message(e)
    match = msgMatcher.match(msg)
    if None is match:
        return False
    grp = match.group()
    return grp == msg


def clear_intermediate_errors() -> None:
    """
    Clear so far recorded records - those are considered intermediate and resolved.

    For example after successful completion of a step.
    # TODO: better keep errors in context and not globally!
    """
    BLAMEES.clear()
