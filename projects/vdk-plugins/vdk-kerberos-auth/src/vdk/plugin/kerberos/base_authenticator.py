# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from abc import ABC
from abc import abstractmethod

from vdk.internal.control.exception.vdk_exception import VDKException

log = logging.getLogger(__name__)


class BaseAuthenticator(ABC):
    def __init__(
        self,
        keytab_pathname: str,
        kerberos_principal: str,
        kerberos_realm: str = None,
        kerberos_kdc_hostname: str = None,
    ):

        if not os.path.isfile(keytab_pathname):
            f = os.path.abspath(keytab_pathname)
            log.warning(
                f"Cannot locate keytab file {keytab_pathname}. File does not exist. "
                f"Kerberos authentication is impossible, I'll rethrow this error for processing "
                f"by my callers and they will decide whether they can recover or not. "
                f"To avoid this message in the future, please ensure a keytab file at {f}"
            )
            raise VDKException(
                what="Cannot locate keytab file",
                why=f"Keytab file at {f} does not exist",
                consequence="Subsequent operation that require authentication will fail.",
                countermeasure=f"Ensure a keytab file is located at {f}.",
            )
        self._keytab_pathname = os.path.abspath(keytab_pathname)
        self._kerberos_principal = kerberos_principal
        self._kerberos_realm = kerberos_realm
        self._kerberos_kdc_hostname = kerberos_kdc_hostname
        self._is_authenticated = False

        self.__configure_krb5_config()

    def __str__(self):
        return str(self.__repr__())

    @staticmethod
    def __configure_krb5_config():
        kerberos_module_dir = os.path.dirname(os.path.abspath(__file__))
        krb5_conf_path = os.path.join(kerberos_module_dir, "krb5.conf")
        if os.path.exists(krb5_conf_path):
            os.environ["KRB5_CONFIG"] = krb5_conf_path

    def authenticate(self):
        if not self.is_authenticated():
            if self._kinit():
                self.set_authenticated()
        else:
            log.debug(
                f"Already authenticated, skipping authentication for principal {self._kerberos_principal}."
            )

    def get_principal(self):
        return self._kerberos_principal

    def is_authenticated(self):
        # TODO add support for renewal
        return self._is_authenticated

    def set_authenticated(self):
        # TODO add support for renewal
        self._is_authenticated = True

    @abstractmethod
    def _kinit(self):
        pass
