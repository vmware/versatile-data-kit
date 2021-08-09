import functools


class LogDecorator(object):
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
                self.logger.debug("Exception {0}".format(ex))
                raise

        return decorated

