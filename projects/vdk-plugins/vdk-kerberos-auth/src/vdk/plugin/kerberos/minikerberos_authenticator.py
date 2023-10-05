# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import asyncio
import logging
import os
import tempfile
import threading

from minikerberos.common.creds import KerberosCredential
from minikerberos.common.target import KerberosTarget
from vdk.internal.core import errors
from vdk.internal.core.errors import ResolvableBy
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

        krb5ccname = os.environ.get("KRB5CCNAME", None)
        if krb5ccname and krb5ccname.startswith("FILE:"):
            log.debug("FILE type KRB5CCNAME set and will reuse it.")
            self._ccache_file = os.environ["KRB5CCNAME"].split(":", 1)[1]
        else:
            log.debug("Will set its own KRB5CCNAME.")
            self._ccache_file = tempfile.NamedTemporaryFile(
                prefix="vdkkrb5cc", delete=True
            ).name
            os.environ["KRB5CCNAME"] = "FILE:" + self._ccache_file
        log.debug(f"KRB5CCNAME is set to a file {self._ccache_file}")

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

    import asyncio

    @staticmethod
    def _run_coroutine(coroutine):
        """
        Executes the given coroutine, ensuring that it runs to completion, even if called within an already running event loop.

        If called within a running event loop, this function will start a new thread to execute the coroutine.

        :param coroutine: The coroutine to execute.
        :return: The result of the coroutine execution if the loop is not running. None otherwise.
        """
        result = None
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():

                def run_in_new_thread():
                    nonlocal result
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(coroutine)

                thread = threading.Thread(target=run_in_new_thread)
                thread.start()
                thread.join()
            else:
                result = loop.run_until_complete(coroutine)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(coroutine)
        return result

    def _kinit(self) -> None:
        log.debug(
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

            self._run_coroutine(get_tgt())
            log.debug(f"krb_client is {krb_client}")

            krb_client.ccache.to_file(self._ccache_file)
            log.debug(
                f"Got Kerberos TGT for {self._kerberos_principal}@{self._kerberos_realm} "
                f"and stored to file: {self._ccache_file}"
            )
        except Exception as e:
            log.warning("Could not retrieve Kerberos TGT")
            errors.report_and_rethrow(ResolvableBy.CONFIG_ERROR, e)
