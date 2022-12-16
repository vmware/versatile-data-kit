# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from threading import Thread
from typing import Any


class HealthCheckServer:
    def __init__(self, port: int, handler: Any = None):
        if handler:
            self._server = HTTPServer(("", port), handler)
        else:
            self._server = HTTPServer(("", port), SimpleHTTPRequestHandler)
        self._thread = Thread(target=self._server.serve_forever)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, typ, value, traceback):
        self.stop()

    def start(self):
        self._thread.start()

    def stop(self):
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()
