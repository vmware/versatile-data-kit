# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import sys
import threading
import traceback
from http.server import BaseHTTPRequestHandler

from vdk.internal.core.config import Configuration
from vdk.plugin.jobs_troubleshoot.api.troubleshoot_utility import ITroubleshootUtility
from vdk.plugin.jobs_troubleshoot.troubleshoot_configuration import (
    TROUBLESHOOT_PORT_TO_USE,
)
from vdk.plugin.jobs_troubleshoot.troubleshoot_utilities.healthcheck_server import (
    HealthCheckServer,
)

log = logging.getLogger(__name__)


class ThreadDumpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/threads":
            self.send_response(200)
            self.wfile.write(b"making a thread dump")
            log.info("Dumping threads")
            self._log_thread_dump()
        else:
            self.send_error(404)

    @staticmethod
    def _log_thread_dump():
        try:
            for t in threading.enumerate():
                log.info(
                    f"Thread:{t.getName()} alive:{t.is_alive()} daemon:{t.isDaemon()}"
                )
            log.info("--------------------------------------------------------------")
            log.info("Dumping threads stacks:")
            code = []
            for threadId, stack in sys._current_frames().items():
                code.append("\n# ThreadID: %s" % threadId)
                for filename, lineno, name, line in traceback.extract_stack(stack):
                    code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
                    if line:
                        code.append("  %s" % (line.strip()))
            log.info(f"Threads stacks:{json.dumps(code)}")
            log.info("--------------------------------------------------------------")
        except Exception as e:
            log.exception(f"test_reporter_thread exception:{e}", exc_info=True)


class ThreadDumpUtility(ITroubleshootUtility):
    def __init__(self, job_configuration: Configuration):
        self.port_to_use = job_configuration.get_value(TROUBLESHOOT_PORT_TO_USE)
        self.server = HealthCheckServer(self.port_to_use, ThreadDumpHandler)

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()
