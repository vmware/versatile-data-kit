# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0


def is_kerberos_installed():
    """
    If Kerberos is installed we try to authenticate with it.
    """
    try:
        import kerberos

        return True
    except ImportError:
        return False


class KerberosTicket:
    """
    Borrowed from http://python-notes.curiousefficiency.org/en/latest/python_kerberos.html
    """

    def __init__(self, service):
        import kerberos

        __, krb_context = kerberos.authGSSClientInit(service)
        kerberos.authGSSClientStep(krb_context, "")
        self._krb_context = krb_context
        self.auth_header = "Negotiate " + kerberos.authGSSClientResponse(krb_context)

    def verify_response(self, auth_header):
        # Handle comma-separated lists of authentication fields
        for field in auth_header.split(","):
            kind, __, details = field.strip().partition(" ")
            if kind.lower() == "negotiate":
                auth_details = details.strip()
                break
        else:
            raise ValueError("Negotiate not found in %s" % auth_header)
        # Finish the Kerberos handshake
        krb_context = self._krb_context
        if krb_context is None:
            raise RuntimeError("Ticket already used for verification")
        self._krb_context = None
        import kerberos

        kerberos.authGSSClientStep(krb_context, auth_details)
        kerberos.authGSSClientClean(krb_context)
