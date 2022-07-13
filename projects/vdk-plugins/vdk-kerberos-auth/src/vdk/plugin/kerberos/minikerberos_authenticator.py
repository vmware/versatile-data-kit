# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import asyncio
import logging
import os
import tempfile

from minikerberos.common.creds import KerberosCredential
from minikerberos.common.target import KerberosTarget
from vdk.internal.core import errors
from vdk.plugin.kerberos.base_authenticator import BaseAuthenticator
from vdk.plugin.kerberos.vdk_kerberos_client import VdkAioKerberosClient

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
            krb_target = KerberosTarget(self._kerberos_kdc_hostname)
            krb_client = VdkAioKerberosClient(krb_credentials, krb_target)

            async def get_tgt():
                await krb_client.get_TGT()

            # Create a separate event loop and run minikerberos coroutines in it
            # to avoid interfering with other plugins or with data jobs that
            # rely on asyncio functionality, as well. The steps of the process
            # are as follows:
            # 1) Create a new event loop which is different from the default one
            # 2) Execute the `get_tgt()` coroutine and wait until it is
            #    finished.
            # 3) After the kerberos TGT is retrieved and the coroutine has
            #    finished, close the event loop. As it is a single coroutine,
            #    we don't really need to do anything else.
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(get_tgt())
            finally:
                loop.close()

            krb_client.ccache.to_file(self._ccache_file)
            log.info(
                f"Got Kerberos TGT for {self._kerberos_principal}@{self._kerberos_realm} "
                f"and stored to file: {self._ccache_file}"
            )
        except Exception as e:
            errors.log_and_rethrow(
                to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                log=log,
                what_happened="Could not retrieve Kerberos TGT",
                why_it_happened=str(e),
                consequences="Kerberos authentication will fail, and as a result the current process will fail.",
                countermeasures="See stdout for details and fix the code, so that getting the TGT succeeds. "
                "If you have custom Kerberos settings, set through environment variables make sure they are correct.",
                exception=e,
                wrap_in_vdk_error=True,
            )
