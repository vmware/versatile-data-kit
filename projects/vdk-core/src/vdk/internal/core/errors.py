# Copyright 2021-2023 VMware, Inc.
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
from logging import Logger

log = logging.getLogger(__name__)


# ERROR TYPES


class BaseVdkError(Exception):
    def __init__(
        self,
        vdk_resolvable_actual: ResolvableByActual = None,
        resolvable_by: ResolvableBy = None,
        *error_message_lines: str,
    ):
        """
        :param vdk_resolvable_actual: who should resolve the error (User or Platform Team)
        :param resolvable_by: the vdk error type, e.g. Platform, User or Config error
        :param *error_message_lines: optional, the error message lines used to build the error representation
        """

        # Check if error message or dict was passed
        # for compatibility with vdk plugins
        self._line_delimiter = " "
        self._header = f"{self.__class__.__name__}: Error of resolvable type {resolvable_by} occurred."
        error_message = self._header + self._line_delimiter
        if error_message_lines and isinstance(error_message_lines[0], ErrorMessage):
            message = error_message_lines[0]
            error_message += self._line_delimiter.join(
                [
                    message.summary,
                    message.what,
                    message.why,
                    message.consequences,
                    message.countermeasures,
                ]
            )
        elif error_message_lines and isinstance(error_message_lines[0], dict):
            message = error_message_lines[0]
            error_message += self._line_delimiter.join(message.values())
        else:
            error_message += self._line_delimiter.join(error_message_lines)
        super().__init__(error_message)
        self._vdk_resolvable_by = resolvable_by
        self._vdk_resolvable_actual = vdk_resolvable_actual
        self._pretty_message = error_message
        # TODO: Enable this for local runs only
        # self._prettify_message(str(error_message))

    def __str__(self):
        return self._pretty_message

    def __repr__(self):
        return self._pretty_message

    def _prettify_message(self, message):
        """
        :param message: the error message string that should be prettified

        Creates a box with a header and body around the error message.
        The header contains the error class name, the error type and
        who should resolve the error. The body contains the actual error
        message. The box length is determined by the header lenght. Lines
        in the body that are longer than the header are wrapped on the
        first space before the max length cutoff.

        Example:

            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            +   VdkConfigurationError: An error of type Configuration error occurred. Error should be fixed by Platform   +
            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            +  Provided configuration variable for DB_DEFAULT_TYPE has invalid value.                                     +
            +  VDK was run with DB_DEFAULT_TYPE=sqlite, however sqlite is invalid value for this variable.                +
            +  I'm rethrowing this exception to my caller to process.Most likely this will result in failure of           +
            +  current Data Job.                                                                                          +
            +  Provide either valid value for DB_DEFAULT_TYPE or install database plugin that supports this type.         +
            +  Currently possible values are []                                                                           +
            +                                                                                                             +
            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        """
        box_char = "+"
        lines = message.split(self._line_delimiter)
        max_len = len(self._header)
        # Wrap the message lines
        wrapped_lines = []
        for line in lines:
            # Find the nearest space if a line is
            # longer than the header and wrap around it
            # Do this until the remainder of the line is shorter
            # than the header
            if len(line) > max_len:
                l = line
                while len(l) > max_len:
                    br = max_len
                    while l[br] != " " and br > 0:
                        br -= 1
                    if br == 0:
                        br = max_len
                    wrapped_lines.append(l[: br + 1])
                    l = l[br + 1 :]
                wrapped_lines.append(l)
            else:
                wrapped_lines.append(line)
        # build th header
        self._header = box_char + self._header.center(max_len + 6) + box_char
        # build the lines with the box char
        lines = [
            box_char + "  " + s.ljust(max_len + 4) + box_char for s in wrapped_lines
        ]
        # build the box sides
        side = (max_len + 8) * box_char
        self._pretty_message = "\n".join(
            ["\n" + side, self._header, side, "\n".join(lines), side]
        )


class SkipRemainingStepsException(BaseVdkError):
    """
    An exception used to skip the remaining steps of a Data Job.

    When this exception is thrown from a data job python step, all the other steps will
    be skipped and the data job execution will exit and be marked as success.
    """

    def __init__(self, *error_message_lines: str):
        super().__init__(None, None, *error_message_lines)


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
    setattr(exception, "_vdk_resolvable_by", resolvable_by)
    setattr(
        exception,
        "_vdk_resolvable_actual",
        __error_type_to_actual_resolver(resolvable_by),
    )


def get_exception_resolvable_by(exception: BaseException):
    if hasattr(exception, "_vdk_resolvable_by"):
        return getattr(exception, "_vdk_resolvable_by")
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


# REPORTING


def log_exception(log: Logger, exception: BaseException, *lines: str) -> None:
    """
    Log message and exception
    """
    message = "\n".join([s for s in lines if s])
    log.warning(message)
    log.exception(exception)


def report(error_type: ResolvableBy, exception: BaseException):
    set_exception_resolvable_by(exception, error_type)
    resolvable_context().add(
        Resolvable(
            error_type,
            get_exception_resolvable_by_actual(exception),
            str(exception),
            exception,
        )
    )


def report_and_throw(
    exception: BaseVdkError,
    resolvable_by: ResolvableBy = None,
    cause: BaseException = None,
) -> None:
    """
    Add exception to resolvable context and then throw it to be handled up the stack.
    """
    if resolvable_by:
        set_exception_resolvable_by(exception, resolvable_by)

    resolvable_context().add(
        Resolvable(
            get_exception_resolvable_by(exception),
            get_exception_resolvable_by_actual(exception),
            str(exception),
            exception,
        )
    )
    raise exception from cause


def report_and_rethrow(error_type: ResolvableBy, exception: BaseException) -> None:
    """
    Add exception to resolvable context and then throw it to be handled up the stack.
    """
    report(error_type, exception)
    raise exception


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


# COMPATIBILITY


def log_and_throw(
    to_be_fixed_by: ResolvableBy,
    log: Logger,
    what_happened: str,
    why_it_happened: str,
    consequences: str,
    countermeasures: str,
) -> None:
    """
    Deprecated: "Use report_and_throw and do the logging separately"

    log_and_throw kept for compatibility of plugins with older version of vdk-core
    """
    message = [what_happened, why_it_happened, consequences, countermeasures]
    if to_be_fixed_by == ResolvableBy.USER_ERROR:
        report_and_throw(UserCodeError(*message))
    if to_be_fixed_by == ResolvableBy.PLATFORM_ERROR:
        report_and_throw(PlatformServiceError(*message))
    if to_be_fixed_by == ResolvableBy.CONFIG_ERROR:
        report_and_throw(VdkConfigurationError(*message))


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
    Deprecated: Use report_and_rethrow and do the logging separately

    log_and_rethrow kept for compatibility of plugins with older version of vdk-core
    """
    if wrap_in_vdk_error:
        pass
        # wrap
    message = [what_happened, why_it_happened, consequences, countermeasures]
    log.error("\n".join(message))
    report_and_rethrow(to_be_fixed_by, exception)


class ErrorMessage:
    """
    Deprecated: Pass the error message lines to the vdk exception directly

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


class DomainError(BaseVdkError):
    """
    Deprecated: Use BaseVdkError directly or extend BaseVdkError into a domain-specific class
    """

    pass


class PlatformServiceError(BaseVdkError):
    """
    Deprecated: Use BaseVdkError directly or extend BaseVdkError into a domain-specific class

    Error caused by issue in Platform

    Service error are those errors which indicate for bad condition of the service. which prevent the normal
    completion of given request. User can do little more beyond retrying.
    """

    def __init__(self, *error_message_lines: str):
        super().__init__(
            ResolvableByActual.PLATFORM,
            ResolvableBy.PLATFORM_ERROR,
            *error_message_lines,
        )


class VdkConfigurationError(BaseVdkError):
    """
    Deprecated: Use BaseVdkError directly or extend BaseVdkError into a domain-specific class

    An exception in the configuration of the Data Job

    If job is executed on user (local execution) premises - this is considered #RESOLVED_BY_JOB_OWNER
    Otherwise If job is executed in "cloud" - this is considered #RESOLVED_BY_PLATFORM class of error
    """

    def __init__(self, *error_message_lines: str):
        super().__init__(
            CONFIGURATION_ERRORS_ARE_TO_BE_RESOLVED_BY,
            ResolvableBy.CONFIG_ERROR,
            *error_message_lines,
        )


class UserCodeError(BaseVdkError):
    """
    Deprecated: Use BaseVdkError directly or extend BaseVdkError into a domain-specific class

    Error caused by issue in user code
    """

    def __init__(self, *error_message_lines: str):
        super().__init__(
            ResolvableByActual.USER, ResolvableBy.USER_ERROR, *error_message_lines
        )
