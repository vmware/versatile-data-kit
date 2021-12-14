# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import tempfile

from minikerberos.common import KerberosCredential
from minikerberos.communication import KerberosSocket
from minikerberos.communication import KerbrosComm
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.core import errors


class MinikerberosGSSAPIAuthenticator:
    def __init__(
        self,
        keytab_pathname: str,
        kerberos_principal: str,
        kerberos_realm: str,
        kerberos_kdc_hostname: str,
    ):
        self._log = logging.getLogger(__name__)
        if not os.path.isfile(keytab_pathname):
            f = os.path.abspath(keytab_pathname)
            self._log.warning(
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

        self._ccache_file = tempfile.NamedTemporaryFile(
            prefix="vdkkrb5cc", delete=True
        ).name
        os.environ["KRB5CCNAME"] = "FILE:" + self._ccache_file
        self._log.info(f"KRB5CCNAME is set to a new file {self._ccache_file}")

    def __repr__(self):
        return {
            "kerberos_principal": self._kerberos_principal,
            "kerberos_realm": self._kerberos_realm,
            "keytab_pathname": self._keytab_pathname,
            "kerberos_kdc_hostname": self._kerberos_kdc_hostname,
            "is_authenticated": self._is_authenticated,
        }

    def __str__(self):
        return str(self.__repr__())

    def authenticate(self):
        if not self.is_authenticated():
            if self.__kinit():
                self.set_authenticated()
        else:
            self._log.debug(
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

    @staticmethod
    def __configure_krb5_config():
        kerberos_module_dir = os.path.dirname(os.path.abspath(__file__))
        krb5_conf_path = os.path.join(kerberos_module_dir, "krb5.conf")
        if os.path.exists(krb5_conf_path):
            os.environ["KRB5_CONFIG"] = krb5_conf_path

    def __exit__(self, *exc):
        try:
            os.remove(self._ccache_file)
        except:
            pass

    def __kinit(self):
        self._log.info(
            "Getting kerberos TGT for principal: %s, realm: %s using keytab file: %s from kdc: %s",
            self._kerberos_principal,
            self._kerberos_realm,
            self._keytab_pathname,
            self._kerberos_kdc_hostname,
        )
        try:
            krb_credentials = KerberosCredential.from_keytab(
                self._keytab_pathname, self._kerberos_principal, self._kerberos_realm
            )
            krb_socket = KerberosSocket(self._kerberos_kdc_hostname)
            krb_comm = KerbrosComm(krb_credentials, krb_socket)
            krb_comm.get_TGT()
            krb_comm.ccache.to_file(self._ccache_file)
            self._log.info(
                f"Got Kerberos TGT for {self._kerberos_principal}@{self._kerberos_realm} "
                f"and stored to file: {self._ccache_file}"
            )
            return self._ccache_file
        except Exception as e:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                log=self._log,
                what_happened="Could not retrieve Kerberos TGT",
                why_it_happened=str(e),
                consequences="Kerberos authentication will fail, and as a result the current process will fail.",
                countermeasures="See stdout for details and fix the code, so that getting the TGT succeeds. "
                "If you have custom Kerberos settings, set through environment variables make sure they are correct.",
            )
