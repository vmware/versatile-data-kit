# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import subprocess  # nosec
import time
from unittest import mock

import pytest
from vdk.plugin.test_utils.util_funcs import get_caller_directory


krb5_realm = "EXAMPLE.COM"
krb5_user = "admin/admin"
krb5_pass = "iamaserver"  # nosec


def _run_kadmin_query(query) -> int:
    # no untrusted input can appear here
    return subprocess.run(  # nosec
        [
            "kadmin",
            "-p",
            krb5_user,
            "-w",
            krb5_pass,
            "-q",
            query,
        ]
    ).returncode


def _is_responsive():
    try:
        return _run_kadmin_query("list_principals") == 0
    except:
        return False


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "docker-compose.yml"
    )


@pytest.fixture(scope="session")
def kerberos_service(docker_ip, docker_services):
    """
    Ensure that Kerberos server is up and responsive.
    Do a post-startup server configuration.
    """

    # give the server some time to start before checking if it is ready
    # before adding this sleep there were intermittent fails of the CI/CD with error:
    # requests.exceptions.ConnectionError:
    #   ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
    # More info: https://stackoverflow.com/questions/383738/104-connection-reset-by-peer-socket-error-or-when-does-closing-a-socket-resu
    time.sleep(1)

    caller_directory = get_caller_directory()
    with mock.patch.dict(
        os.environ,
        {
            "KRB5_CONFIG": str(caller_directory.joinpath("krb5.conf")),
        },
    ):
        docker_services.wait_until_responsive(
            timeout=90.0, pause=0.3, check=_is_responsive
        )

        # Add the data job principal to the Kerberos server and obtain a keytab for it.
        # Realm and pass are the same as those configured at server startup (see ./docker-compose.yml)
        datajob_name = "test-job"
        keytab_filename = (
            caller_directory.joinpath("jobs")
            .joinpath(datajob_name)
            .joinpath("test-job.keytab")
        )
        if os.path.isfile(keytab_filename):
            os.remove(keytab_filename)
        result = _run_kadmin_query(f"add_principal -randkey pa__view_{datajob_name}")
        assert result == 0, "(kadmin) failed to create principal"
        result = _run_kadmin_query(
            f"ktadd -k {keytab_filename} pa__view_{datajob_name}@{krb5_realm}"
        )
        assert result == 0, "(kadmin) failed to create keytab"
