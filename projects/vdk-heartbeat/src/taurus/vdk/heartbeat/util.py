# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from contextlib import contextmanager
from typing import TypeVar

log = logging.getLogger(__name__)

T = TypeVar("T")


@contextmanager
def closing_noexcept_on_close(thing: T) -> T:
    try:
        yield thing
    finally:
        try:
            thing.close()
        except Exception as e:
            log.info(
                f"Failed to close {thing}. This is not an issue. Will ignore it and continue. Exception was '{e}'."
            )
            pass
