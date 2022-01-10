# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time
from subprocess import call  # nosec
from unittest import mock

import pytest
from vdk.plugin.test_utils.util_funcs import get_caller_directory


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "docker-compose.yml"
    )


@pytest.fixture(scope="session")
def kerberos_service(docker_ip, docker_services):
    """Ensure that Kerberos server is up and responsive."""
    time.sleep(10)

    # Add the data job principal to the Kerberos server and obtain a keytab for it.
    # Realm and pass are the same as those configured at server startup (see ./docker-compose.yml)
    caller_directory = get_caller_directory()
    datajob_name = "test-job"
    keytab_filename = (
        caller_directory.joinpath("jobs")
        .joinpath(datajob_name)
        .joinpath("test-job.keytab")
    )
    krb5_realm = "EXAMPLE.COM"
    krb5_pass = "iamaserver"  # nosec
    with mock.patch.dict(
        os.environ,
        {
            "KRB5_CONFIG": str(caller_directory.joinpath("krb5.conf")),
        },
    ):
        if os.path.isfile(keytab_filename):
            os.remove(keytab_filename)
        call(  # nosec
            [
                "kadmin",
                "-p",
                "admin/admin",
                "-w",
                krb5_pass,
                "-q",
                f"add_principal -randkey pa__view_{datajob_name}",
            ]
        )
        call(  # nosec
            [
                "kadmin",
                "-p",
                "admin/admin",
                "-w",
                krb5_pass,
                "-q",
                f"ktadd -k {keytab_filename} pa__view_{datajob_name}@{krb5_realm}",
            ]
        )
