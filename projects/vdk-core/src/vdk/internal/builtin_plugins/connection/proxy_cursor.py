# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import types
from typing import Any

from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor


class ProxyCursor(PEP249Cursor):
    """
    PEP249 Proxy cursor.
    It wraps all methods and proxies (non-override methods) to the passed native cursor.
    Allowing the wrapped cursor to be used as a native cursor as well for native (vendor specific) methods.

    """

    def __init__(self, cursor: Any, log: logging.Logger = logging.getLogger(__name__)):
        super().__init__(cursor, log)

    def __getattr__(self, attr):
        """
        Dynamic interception and il of any (non-overridden) attribute access.
        In case an attribute is not explicitly managed (customized by overriding e.g. execute()) -
        this attribute is looked up then the call is delegated, ensuring default behaviour success path.

        First, the non-managed attribute call is redirected to the wrapped native cursor if attribute available,
        otherwise to the superclass if attribute is present.
        If the attribute is not specified by both the native cursor nor the superclass, an AttributeError is raised.

        Default behaviour availability unblocks various ManagedCursor usages that rely on
        currently not explicitly defined in the scope of ManagedCursor attributes.
        E.g. SQLAlchemy dependency that uses the ManagedCursor, does require some specific attributes available.

        For more details on customizing attributes access, see PEP562.
        """
        # native cursor
        if hasattr(self._cursor, attr):
            if isinstance(getattr(self._cursor, attr), types.MethodType):

                def method(*args, **kwargs):
                    return getattr(self._cursor, attr)(*args, **kwargs)

                return method
            return getattr(self._cursor, attr)
        # superclass
        if hasattr(super(), attr):
            if isinstance(getattr(super(), attr), types.MethodType):

                def method(*args, **kwargs):
                    return getattr(super(), attr)(*args, **kwargs)

                return method
            return getattr(super(), attr)
        raise AttributeError
