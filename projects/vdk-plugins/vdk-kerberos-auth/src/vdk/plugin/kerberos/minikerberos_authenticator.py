# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import tempfile

from minikerberos.common import KerberosCredential
from minikerberos.communication import KerberosSocket
from minikerberos.communication import KerbrosComm
from vdk.internal.core import errors
from vdk.plugin.kerberos.base_authenticator import BaseAuthenticator

log = logging.getLogger(__name__)


class MinikerberosGSSAPIAuthenticator(BaseAuthenticator):
    """
    A Kerberos authenticator that connects directly to the KDC (using the minikerberos library)
    to get its ticket-granting ticket (TGT).
    """

    def __init__(
        self,
        krb5_conf_filename: str,
        keytab_pathname: str,
        kerberos_principal: str,
        kerberos_realm: str,
        kerberos_kdc_hostname: str,
    ):
        super().__init__(
            krb5_conf_filename,
            keytab_pathname,
            kerberos_principal,
            kerberos_realm,
            kerberos_kdc_hostname,
        )

        self._ccache_file = tempfile.NamedTemporaryFile(
            prefix="vdkkrb5cc", delete=True
        ).name
        os.environ["KRB5CCNAME"] = "FILE:" + self._ccache_file
        log.info(f"KRB5CCNAME is set to a new file {self._ccache_file}")

    def __repr__(self):
        return {
            "kerberos_principal": self._kerberos_principal,
            "kerberos_realm": self._kerberos_realm,
            "keytab_pathname": self._keytab_pathname,
            "kerberos_kdc_hostname": self._kerberos_kdc_hostname,
            "is_authenticated": self._is_authenticated,
        }

    def __exit__(self, *exc):
        try:
            os.remove(self._ccache_file)
        except OSError:
            pass

    def _kinit(self) -> None:
        log.info(
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
            log.info(
                f"Got Kerberos TGT for {self._kerberos_principal}@{self._kerberos_realm} "
                f"and stored to file: {self._ccache_file}"
            )
        except Exception as e:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                log=log,
                what_happened="Could not retrieve Kerberos TGT",
                why_it_happened=str(e),
                consequences="Kerberos authentication will fail, and as a result the current process will fail.",
                countermeasures="See stdout for details and fix the code, so that getting the TGT succeeds. "
                "If you have custom Kerberos settings, set through environment variables make sure they are correct.",
            )
