# Copyright 2021 VMware, Inc.
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
        self._cursor = cursor
        self._log = log

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def callproc(self, procname, parameters=None):
        return self._cursor.callproc(procname, parameters)

    def close(self):
        return self._cursor.close()

    def execute(self, operation, parameters=None):
        if parameters:
            return self._cursor.execute(operation, parameters)
        return self._cursor.execute(operation)

    def executemany(self, operation, seq_of_parameters):
        return self._cursor.executemany(operation, seq_of_parameters)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchmany(self, size=None):
        return self._cursor.fetchmany(size)

    def fetchall(self):
        return self._cursor.fetchall()

    def nextset(self):
        return self._cursor.nextset()

    def _get_arraysize(self):
        return self._cursor._get_arraysize()

    def _set_arraysize(self, arraysize):
        return self._cursor._set_arraysize()

    arraysize = property(_get_arraysize, _set_arraysize)

    def setinputsizes(self, sizes):
        return self._cursor.setinputsizes(sizes)

    def setoutputsize(self, size, column=None):
        return self._cursor.setoutputsize(size, column)

    def __iter__(self):
        return self._cursor.__iter__()

    def __next__(self):
        return self._cursor.__next__()

    def next(self):
        # for py2 compat
        return self.__next__()
