# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import tempfile
from subprocess import call

from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.core import errors


class KinitGSSAPIAuthenticator:
    def __init__(self, keytab_pathname, kerberos_principal, working_dir=None):
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
        self._is_authenticated = False
        self._working_dir = working_dir
        self.__configure_current_os_process_to_use_own_kerberos_credentials_cache()
        self.__configure_krb5_config()

    def __repr__(self):
        return {
            "principal": self._kerberos_principal,
            "keytab_pathname": self._keytab_pathname,
        }

    def __str__(self):
        return str({"principal": self._kerberos_principal})

    def __exit__(self, *exc):
        self.__restore_previous_os_process_kerberos_credentials_cache_configuration()
        try:
            os.remove(self._tmp_file)
        except:
            pass

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

    def __configure_current_os_process_to_use_own_kerberos_credentials_cache(self):
        try:
            self._oldKRB5CCNAME = os.environ[
                "KRB5CCNAME"
            ]  # used for deleting the env variable later
            self._log.info(f"KRB5CCNAME was already set to {self._oldKRB5CCNAME}")
        except KeyError:
            tmpfile = tempfile.mktemp(prefix="vdkkrb5cc", dir=self._working_dir)
            os.environ["KRB5CCNAME"] = "FILE:" + tmpfile
            self._log.info(f"KRB5CCNAME is set to a new file {tmpfile}")
            self._tmp_file = tmpfile

    def __restore_previous_os_process_kerberos_credentials_cache_configuration(self):
        if hasattr(self, "_oldKRB5CCNAME"):
            os.environ["KRB5CCNAME"] = self._oldKRB5CCNAME
            self._log.info(f"KRB5CCNAME is restored to {self._oldKRB5CCNAME}")
            del self._oldKRB5CCNAME
        else:
            del os.environ["KRB5CCNAME"]
            self._log.info("KRB5CCNAME is now unset")
            try:
                os.remove(self._tmp_file)
            except:
                pass

    @staticmethod
    def __configure_krb5_config():
        kerberos_module_dir = os.path.dirname(os.path.abspath(__file__))
        krb5_conf_path = os.path.join(kerberos_module_dir, "krb5.conf")
        if os.path.exists(krb5_conf_path):
            os.environ["KRB5_CONFIG"] = krb5_conf_path

    def __kinit(self):
        self._log.info(
            f"Calling kinit for kerberos principal {self._kerberos_principal} and keytab file {self._keytab_pathname}"
        )
        exitcode = call(
            ["kinit", "-k", "-t", self._keytab_pathname, self._kerberos_principal]
        )
        if 0 == exitcode:
            return True
        else:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                log=self._log,
                what_happened="Could not execute kinit",
                why_it_happened=f"kinit returned exitcode {str(exitcode)}",
                consequences="Kerberos authentication will fail, and as a result the current process will fail.",
                countermeasures="See stdout for details and fix the code, so that kinit succeeds. "
                "Make sure you have the correct krb5.conf file and set the "
                "KRB5_CONFIG environment variable to point to it: "
                "KRB5_CONFIG=XXX/krb5.conf. If the krb5.conf is located at "
                "/etc/krb5.conf (on linux) then you don't need to set the environment variable.",
            )
