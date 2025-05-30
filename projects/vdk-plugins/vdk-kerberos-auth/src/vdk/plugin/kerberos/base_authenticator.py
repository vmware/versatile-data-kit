# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from abc import ABC
from abc import abstractmethod

from vdk.internal.core import errors
from vdk.internal.core.errors import VdkConfigurationError

log = logging.getLogger(__name__)


class BaseAuthenticator(ABC):
    def __init__(
        self,
        krb5_conf_filename: str,
        keytab_pathname: str,
        kerberos_principal: str,
        kerberos_realm: str = None,
        kerberos_kdc_hostname: str = None,
    ):
        if not os.path.isfile(keytab_pathname):
            f = os.path.abspath(keytab_pathname)
            errors.report_and_throw(
                VdkConfigurationError(
                    f"Cannot locate keytab file {keytab_pathname}.",
                    f"Keytab file at {f} does not exist",
                    "Kerberos authentication is impossible. "
                    "Subsequent operation that require authentication will fail.",
                    f"Ensure a keytab file is located at {f}.",
                )
            )
        self._krb5_conf_filename = krb5_conf_filename
        self._keytab_pathname = os.path.abspath(keytab_pathname)
        self._kerberos_principal = kerberos_principal
        self._kerberos_realm = kerberos_realm
        self._kerberos_kdc_hostname = kerberos_kdc_hostname
        self._is_authenticated = False

        self.__configure_krb5_config()

    def __str__(self):
        return str(self.__repr__())

    def __configure_krb5_config(self):
        if os.path.exists(self._krb5_conf_filename):
            os.environ["KRB5_CONFIG"] = self._krb5_conf_filename

    def authenticate(self):
        if not self._is_authenticated:
            log.debug(
                f"Starting kerberos authentication for principal {self._kerberos_principal}"
                f" to KDC host {self._kerberos_kdc_hostname}"
                f" at KDC realm {self._kerberos_realm}"
                f" using keytab {self._keytab_pathname}"
            )
            self._kinit()
            self._is_authenticated = True
        else:
            log.debug(
                f"Already authenticated, skipping authentication for principal {self._kerberos_principal}."
            )

    def get_principal(self):
        return self._kerberos_principal

    def is_authenticated(self):
        # TODO add support for renewal
        return self._is_authenticated

    @abstractmethod
    def _kinit(self) -> None:
        """
        Obtain and cache a Kerberos ticket-granting ticket (TGT)
        that will be used for subsequent Kerberos authentication.
        This method either succeeds or throws an exception.
        """
