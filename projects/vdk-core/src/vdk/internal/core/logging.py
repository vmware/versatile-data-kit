# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging


class VdkBoundLogger(logging.LoggerAdapter):
    """
    This class wraps around a Logger to append additional context to log records.
    Logger-wide context can be included by providing it in the `context` parameter of the
    `bind_logger` method.
    Log statement-specific context can be included by including an `extra` kwarg to the log call and
    providing a dictionary object (or any object which implements __getitem__ and __iter__) with the
    required additional log fields.
    It is intended to be instantiated using the `bind_logger` function and providing it with the current
    log object and the additional context which will be included in dictionary form.

    Example use::

        import logging
        from vdk.internal.builtin_plugins.config.log_config import bind_logger

        bound_logger = bind_logger(logging.getLogger(__name__), {"logger_wide_bound_key": "logger_wide_bound_value"})
        bound.warning("From vdk_initialize", extra={"first_key": "first_value"})
        bound.warning("Something else from vdk_initialize")

    Now, the LogRecord produced by the first log statement will have both
    "logger_wide_bound_key": "logger_wide_bound_value" and "first_key": "first_value" included in its __dict__,
    while the second one will only have "first_key": "first_value" in it.

    Note that these will not be automatically included in the output log and must be processed downstream by
    something like vdk-structlog.
    """

    def process(self, msg: str, kwargs: dict):
        # merge bound extra dict with existing extra dict if any
        if "extra" in kwargs:
            kwargs["extra"] = {**self.extra, **kwargs["extra"]}
        else:
            kwargs["extra"] = self.extra
        return msg, kwargs


def bind_logger(log: logging.Logger, context: dict):
    """
    Instantiates a VdkBoundLogger object.

    :param log: current log object
    :param context: dictionary containing the additional context we want to include in log statements
    :return: a VdkBoundLogger instance
    """
    return VdkBoundLogger(log, context)
