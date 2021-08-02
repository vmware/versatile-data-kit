# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging


class PEP249Connection:
    """
    Interface and protocol for PEP 249 compatible connection
    """

    def close(self):
        """PEP 249
        Close the connection now (rather than whenever .__del__() is called).
        The connection will be unusable from this point forward; an Error (or subclass) exception will be raised
        if any operation is attempted with the connection. The same applies to all cursor objects trying to use
        the connection. Note that closing a connection without committing the changes first will cause an
        implicit rollback to be performed.
        """
        raise NotImplementedError

    def commit(self):
        # PEP 249
        raise NotImplementedError

    def rollback(self):
        # PEP 249
        raise NotImplementedError

    def cursor(self):
        """PEP 249
        Return a new Cursor Object using the connection.
        If the database does not provide a direct cursor concept, the module will have to emulate cursors using
        other means to the extent needed by PEP 249 specification.
        """
        raise NotImplementedError


class PEP249Cursor:
    """Abstract representation of Cursor"""

    def __init__(self, cursor, log):
        if not log:
            log = logging.getLogger(__name__)
        self._cur = cursor
        self._log = log

    @property
    def description(self):
        return self._cur.description

    @property
    def rowcount(self):
        return self._cur.rowcount

    def callproc(self, procname, parameters=None):
        return self._cur.callproc(procname, parameters)

    def close(self):
        return self._cur.close()

    def execute(self, operation, parameters=None):
        return self._cur.execute(operation, parameters)

    def executemany(self, operation, seq_of_parameters):
        return self._cur.executemany(operation, seq_of_parameters)

    def fetchone(self):
        return self._cur.fetchone()

    def fetchmany(self, size=None):
        return self._cur.fetchmany(size)

    def fetchall(self):
        return self._cur.fetchall()

    def nextset(self):
        return self._cur.nextset()

    def _get_arraysize(self):
        return self._cur._get_arraysize()

    def _set_arraysize(self, arraysize):
        return self._cur._set_arraysize()

    arraysize = property(_get_arraysize, _set_arraysize)

    def setinputsizes(self, sizes):
        return self._cur.setinputsizes(sizes)

    def setoutputsize(self, size, column=None):
        return self._cur.setoutputsize(size, column)

    def __iter__(self):
        return self._cur.__iter__()

    def __next__(self):
        return self._cur.__next__()

    def next(self):
        # for py2 compat
        return self.__next__()
