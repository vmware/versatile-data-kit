# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import tempfile
from subprocess import call  # nosec

from vdk.internal.core import errors
from vdk.plugin.kerberos.base_authenticator import BaseAuthenticator

log = logging.getLogger(__name__)


class KinitGSSAPIAuthenticator(BaseAuthenticator):
    """
    A Kerberos authenticator that uses a 'kinit' call to obtain its ticket-granting ticket (TGT).
    As this class operates by invoking 'kinit' directly, the Kerberos should be already installed
    on the machine and the 'kinit' command should be working correctly.
    """

    def __init__(
        self, krb5_conf_filename: str, keytab_pathname: str, kerberos_principal: str
    ):
        super().__init__(krb5_conf_filename, keytab_pathname, kerberos_principal)

        self.__configure_current_os_process_to_use_own_kerberos_credentials_cache()

    def __repr__(self):
        return {
            "principal": self._kerberos_principal,
            "keytab_pathname": self._keytab_pathname,
        }

    def __exit__(self, *exc):
        self.__restore_previous_os_process_kerberos_credentials_cache_configuration()
        try:
            os.remove(self._tmp_file)
        except OSError:
            pass

    def __configure_current_os_process_to_use_own_kerberos_credentials_cache(self):
        try:
            self._oldKRB5CCNAME = os.environ[
                "KRB5CCNAME"
            ]  # used for deleting the env variable later
            log.info(f"KRB5CCNAME was already set to {self._oldKRB5CCNAME}")
        except KeyError:
            tmpfile = tempfile.NamedTemporaryFile(prefix="vdkkrb5cc", delete=True).name
            os.environ["KRB5CCNAME"] = "FILE:" + tmpfile
            log.info(f"KRB5CCNAME is set to a new file {tmpfile}")
            self._tmp_file = tmpfile

    def __restore_previous_os_process_kerberos_credentials_cache_configuration(self):
        if hasattr(self, "_oldKRB5CCNAME"):
            os.environ["KRB5CCNAME"] = self._oldKRB5CCNAME
            log.info(f"KRB5CCNAME is restored to {self._oldKRB5CCNAME}")
            del self._oldKRB5CCNAME
        else:
            del os.environ["KRB5CCNAME"]
            log.info("KRB5CCNAME is now unset")
            try:
                os.remove(self._tmp_file)
            except OSError:
                pass

    def _kinit(self) -> None:
        log.info(
            f"Calling kinit for kerberos principal {self._kerberos_principal} and keytab file {self._keytab_pathname}"
        )
        # invoking 'call' here should be safe because:
        # - the input is not directly user-controlled; it depends on the job name,
        #   which has some limitations (no spaces, special characters)
        # - even if the input variables are somehow tapered with, they will be escaped and
        #   no injection will be possible; e.g. if _kerberos_principal is set to
        #   "some_principal; rm -rf *", the entire string will be interpreted as the principal
        exitcode = call(  # nosec
            ["kinit", "-k", "-t", self._keytab_pathname, self._kerberos_principal]
        )
        if exitcode != 0:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                log=log,
                what_happened="Could not execute kinit",
                why_it_happened=f"kinit returned exitcode {str(exitcode)}",
                consequences="Kerberos authentication will fail, and as a result the current process will fail.",
                countermeasures="See stdout for details and fix the code, so that kinit succeeds. "
                "Make sure you have the correct krb5.conf file and set the "
                "KRB5_CONFIG environment variable to point to it: "
                "KRB5_CONFIG=XXX/krb5.conf. If the krb5.conf is located at "
                "/etc/krb5.conf (on linux) then you don't need to set the environment variable.",
            )
