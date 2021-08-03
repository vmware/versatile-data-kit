# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import cast
from typing import Collection
from typing import List
from typing import Tuple
from typing import Union

from taurus.vdk.builtin_plugins.connection.pep249.interfaces import PEP249Cursor


class ManagedCursor(PEP249Cursor):
    """
    PEP249 Cursor
    """

    def __init__(self, cursor: Any, log: logging.Logger = None) -> None:
        if not log:
            log = logging.getLogger(__name__)
        super().__init__(cursor, log)
        self._cur = cursor
        self._log = log

    def execute(
        self, operation: str, parameters: Union[List, Tuple] = None
    ) -> None:  # @UnusedVariable
        self._log.debug("Executing query:\n%s" % operation)
        try:
            if parameters:
                self._cur.execute(operation, parameters)
            else:
                self._cur.execute(operation)
            self._log.debug("Executing query SUCCEEDED.")
        except:
            self._log.debug("Executing query FAILED.")
            raise

    def fetchall(self) -> Collection[Collection[Any]]:
        self._log.debug("Fetching all results from query ...")
        try:
            res = self._cur.fetchall()
            self._log.debug("Fetching all results from query SUCCEEDED.")
            return cast(Collection[Collection[Any]], res)
        except:
            self._log.debug("Fetching all results from query FAILED.")
            raise

    def close(self) -> None:
        self._log.debug("Closing DB cursor ...")
        self._cur.close()
        self._log.debug("Closing DB cursor SUCCEEDED.")
