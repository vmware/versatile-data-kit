# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import pytest
from IPython.testing.globalipapp import get_ipython
from IPython.testing.globalipapp import start_ipython
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext

_log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def session_ip():
    yield start_ipython()


@pytest.fixture(scope="function")
def ip(session_ip):
    session_ip.run_line_magic(magic_name="load_ext", line="vdk_ipython")
    yield session_ip


def test_automatic_finalize_after_kernel_shutdown(ip):
    class FinalizeTrackingPlugin:
        # Due to problems with testing atexit functions, this should be tested manually
        # Logs will be introduced, and to see the result of the test we should check logs
        @hookimpl
        def finalize_job(self, context: JobContext) -> None:
            _log.info("\n\nfinalize_job is called!\n\n")

    plugin = FinalizeTrackingPlugin()
    ip.get_ipython().push(variables={"plugin": plugin})
    ip.run_line_magic(magic_name="reload_VDK", line="")
    ip.get_ipython().run_cell(
        "VDK.job._plugin_registry.load_plugin_with_hooks_impl(plugin)"
    )
    ip.get_ipython().run_cell("job_input = VDK.get_initialized_job_input()")
