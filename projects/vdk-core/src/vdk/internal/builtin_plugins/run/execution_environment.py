# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import functools
import getpass
import logging
import os
import platform
import socket
import sys

log = logging.getLogger(__name__)


class ExecutionEnvironment:
    """
    Information about execution environment - e.g. OS, user, ip, etc.
    """

    def _get_result_noexcept(self, method, property_name):
        try:
            value = method()
        except Exception as e:
            log.debug(
                f"Failed getting {property_name}. Will use unknown instead. Exception: {e} "
            )
            value = "unknown-" + property_name
        return value

    @functools.lru_cache(maxsize=None)
    def get_machine_info(self):
        """
        Get information about the the machine being run on
        Though it's generally better to be split into multiple attributes for telemetry
        But we are putting together not to pollute table schema with too many system columns
        """
        user = self._get_result_noexcept(getpass.getuser, "user")
        ip = self._get_result_noexcept(
            lambda: socket.gethostbyname(socket.gethostname()), "ip"
        )
        host = self._get_result_noexcept(socket.gethostname, "host")
        domain = self._get_result_noexcept(socket.getfqdn, "domain")
        cwd = self._get_result_noexcept(os.getcwd, "cwd")
        os_info = self._get_result_noexcept(platform.platform, "os-info")

        cpu_info = self._get_result_noexcept(lambda: os.cpu_count(), "cpu")
        mem_info = self._get_result_noexcept(
            lambda: os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"), "memory"
        )
        disk_info = self._get_result_noexcept(
            lambda: os.statvfs("/").f_frsize * os.statvfs("/").f_blocks, "disk"
        )

        return f"{user}@{ip}({os_info})({host})({domain})({cwd})({cpu_info}; {mem_info}; {disk_info})"

    @functools.lru_cache(maxsize=None)
    def get_python_version(self):
        """
        Return python version being used to run the job - for example "3.7.9 64bit"
        """
        py_version = self._get_result_noexcept(
            platform.python_version, "python-version"
        )
        py_arch = self._get_result_noexcept(
            lambda: platform.architecture()[0], "python-arch"
        )

        return f"{py_version} {py_arch} ({sys.executable})"
