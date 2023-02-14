# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import subprocess  # nosec
import time
from pathlib import Path
from unittest import mock

import pytest
from pytest_docker.plugin import Services
from vdk.plugin.test_utils.util_funcs import get_caller_directory

krb5_realm = "EXAMPLE.COM"
krb5_user = "admin/admin"
krb5_pass = "iamaserver"  # nosec


def _run_kadmin_query(query) -> int:
    # no untrusted input can appear here
    if os.environ.get("VDK_TEST_USE_KADMIN_DOCKER", "n").lower() in [
        "yes",
        "y",
        "true",
    ]:
        cmd = [
            "docker",
            "run",
            "--network=host",
            "-v",
            f'{os.environ.get("KRB5_CONFIG")}:/etc/krb5.conf',
            "-v",
            f"{str(get_caller_directory())}:/home",
            "tozkata/kadmin",
        ]
    else:
        cmd = ["kadmin"]

    return subprocess.run(  # nosec
        [
            *cmd,
            "-p",
            krb5_user,
            "-w",
            krb5_pass,
            "-q",
            query,
        ],
        cwd=str(get_caller_directory()),
    ).returncode


def _is_responsive():
    return _run_kadmin_query("list_principals") == 0


def _is_responsive_noexcept():
    try:
        return _run_kadmin_query("list_principals") == 0
    except Exception:
        return False


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "docker-compose.yml"
    )


@pytest.fixture(scope="session")
def kerberos_service(docker_ip: str, docker_services: Services):
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
        try:
            docker_services.wait_until_responsive(
                timeout=10.0, pause=0.3, check=_is_responsive_noexcept
            )
        except:
            # check again so we can raise a visible error when something is wrong.
            _is_responsive()

        # Add the data job principal to the Kerberos server and obtain a keytab for it.
        # Realm and pass are the same as those configured at server startup (see ./docker-compose.yml)
        datajob_name = "test-job"
        keytab_filename = Path("jobs").joinpath("test-job.keytab")
        if os.path.isfile(str(caller_directory.joinpath(keytab_filename))):
            os.remove(str(caller_directory.joinpath(keytab_filename)))
        result = _run_kadmin_query(f"add_principal -randkey pa__view_{datajob_name}")
        assert result == 0, "(kadmin) failed to create principal"
        result = _run_kadmin_query(
            f"ktadd -k {keytab_filename} pa__view_{datajob_name}@{krb5_realm}"
        )
        assert result == 0, "(kadmin) failed to create keytab"

        # Create another principal for the purposes of testing wrong credentials later
        keytab_filename2 = Path("jobs").joinpath("different_principal.keytab")
        if os.path.isfile(caller_directory.joinpath(keytab_filename2)):
            os.remove(caller_directory.joinpath(keytab_filename2))
        result = _run_kadmin_query(f"add_principal -randkey different_principal")
        assert result == 0, "(kadmin) failed to create principal"
        result = _run_kadmin_query(
            f"ktadd -k {keytab_filename2} different_principal@{krb5_realm}"
        )
        assert result == 0, "(kadmin) failed to create keytab"
