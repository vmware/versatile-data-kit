# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import functools


class LogDecorator:
    def __init__(self, logger, message=None):
        self.logger = logger
        self.message = message

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            try:
                message = self.message if self.message else fn.__qualname__
                self.logger.debug(f"Starting: {message} ({args},{kwargs})")
                result = fn(*args, **kwargs)
                self.logger.debug(f"Finished: {message}.")
                return result
            except Exception as ex:
                self.logger.debug(f"Exception {ex}")
                raise

        return decorated
