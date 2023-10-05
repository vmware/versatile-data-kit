# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# RESOLVABLE CONTEXT
from __future__ import annotations

import enum
import logging
import re
from collections import defaultdict
from enum import Enum
from logging import Logger

log = logging.getLogger(__name__)


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
