# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
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
    """
    A class for handling HTTP requests and generating thread dumps used by the thread-dump troubleshooting utility.
    """

    def do_GET(self):
        """
        Handles GET requests. If the request path is "/threads", a thread dump is logged and sent as the response.
        Otherwise, a 404 error is sent as the response.
        """
        if self.path == "/threads":
            log.info("Dumping threads")
            self.send_response(200)
            self.send_header("Content-type", "text/plain]")
            self.end_headers()
            self._log_thread_dump()
        else:
            self.send_error(404)

    def _log_thread_dump(self):
        """
        Logs a thread dump and writes it to the response body.
        """
        try:
            log.info("------- Dumping threads stacks -------")
            for t in threading.enumerate():
                log.info(
                    f"Thread:{t.getName()} alive:{t.is_alive()} daemon:{t.isDaemon()}"
                )
                self.wfile.write(
                    str.encode(
                        f"\nThread:{t.getName()} alive:{t.is_alive()} daemon:{t.isDaemon()}"
                    )
                )
            code = []
            for threadId, stack in sys._current_frames().items():
                code.append("# ThreadID: %s" % threadId)
                for filename, lineno, name, line in traceback.extract_stack(stack):
                    code.append(
                        "%s::%d::%s::%s"
                        % (filename, lineno, name, (line.strip() if line else ""))
                    )
            for line in code:
                log.info(line)
                self.wfile.write(str.encode(f"\n {line}"))
            log.info("------- End of thread dump -------")
        except Exception as e:
            log.exception(f"Error while dumping threads:{e}", exc_info=True)


class ThreadDumpUtility(ITroubleshootUtility):
    def __init__(self, job_configuration: Configuration):
        self.port_to_use = job_configuration.get_value(TROUBLESHOOT_PORT_TO_USE)
        self.server = HealthCheckServer(self.port_to_use, ThreadDumpHandler)

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()
