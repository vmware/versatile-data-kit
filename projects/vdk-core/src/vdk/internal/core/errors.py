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

from logging import Logger

from vdk.internal.core.error_classifiers import *

# Due to the expansion of this file's responsibilities over time,
# we've decided to reorganize its contents for better maintainability.
# The logic previously contained here has been moved to a separate module. However, to ensure backward compatibility,
# we are importing all the elements from the new module here.
# This allows existing code to continue functioning without disruption.

log = logging.getLogger(__name__)


# ERROR TYPES


def plain_vdk_error_formatter(ex: BaseVdkError):
    """
    Joins every line of the exception message using space as delimiter.
    This includes the header.

    Example (lines wrapped for convenience):

        vdk.internal.core.errors.VdkConfigurationError: VdkConfigurationError: An error of resolvable type ResolvableByActual.PLATFORM occurred
        Provided configuration variable for DB_DEFAULT_TYPE has invalid value. VDK was run with DB_DEFAULT_TYPE=sqlite, however sqlite is invalid value for this variable.
        I'm rethrowing this exception to my caller to process.Most likely this will result in failure of current Data Job. Provide either valid value for DB_DEFAULT_TYPE or
        install database plugin that supports this type. Currently possible values are []
    """
    ex._lines[0] = ex._lines[0] + "\n"
    ex._pretty_message = " ".join(ex._lines)


def pretty_vdk_error_formatter(ex: BaseVdkError):
    """
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
    lines = ex._lines
    header = lines[0]
    max_len = len(header)
    # Wrap the message lines
    wrapped_lines = []
    for i in range(1, len(lines)):
        line = lines[i]
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
    header = box_char + header.center(max_len + 6) + box_char
    # build the lines with the box char
    lines = [box_char + "  " + s.ljust(max_len + 4) + box_char for s in wrapped_lines]
    # build the box sides
    side = (max_len + 8) * box_char
    ex._pretty_message = "\n".join(["\n" + side, header, side, "\n".join(lines), side])


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
        self._lines = []
        header = f"{self.__class__.__name__}: An error of resolvable type {vdk_resolvable_actual} occurred"
        self._lines.append(header)
        if error_message_lines and isinstance(error_message_lines[0], ErrorMessage):
            message = error_message_lines[0]
            self._lines.extend(
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
            self._lines.extend(message.values())
        else:
            self._lines.extend(error_message_lines)
        super().__init__(str(self._lines))

        self._vdk_resolvable_by = resolvable_by
        self._vdk_resolvable_actual = vdk_resolvable_actual
        self._pretty_message = " ".join(self._lines)

    def __str__(self):
        return self._pretty_message

    def __repr__(self):
        return self._pretty_message

    def _format(self, formatter):
        formatter(self)


class SkipRemainingStepsException(BaseVdkError):
    """
    An exception used to skip the remaining steps of a Data Job.

    When this exception is thrown from a data job python step, all the other steps will
    be skipped and the data job execution will exit and be marked as success.
    """

    def __init__(self, *error_message_lines: str):
        super().__init__(None, None, *error_message_lines)


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
    exception: BaseVdkError, resolvable_by: ResolvableBy = None
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
    raise exception


def report_and_rethrow(error_type: ResolvableBy, exception: BaseException) -> None:
    """
    Add exception to resolvable context and then throw it to be handled up the stack.
    """
    report(error_type, exception)
    raise exception


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
    report(to_be_fixed_by, exception)
    raise exception


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
