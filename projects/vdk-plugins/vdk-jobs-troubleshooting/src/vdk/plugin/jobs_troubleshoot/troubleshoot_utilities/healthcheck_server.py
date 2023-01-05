# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from http.server import HTTPServer
from threading import Thread
from typing import Any

log = logging.getLogger(__name__)


class HealthCheckServer:
    """
    A class for creating an HTTP server for serving requests.
    """

    def __init__(self, port: int, handler: Any = None):
        """
        Initializes a new instance of the HealthCheckServer class.

        Parameters:
            port (int): The port number on which the server will listen for requests.
            handler (Any, optional): The request handler class. Defaults to SimpleHTTPRequestHandler.
        """
        if handler:
            self._server = HTTPServer(("", port), handler)
            self._thread = Thread(target=self._server.serve_forever)
            log.error(f"Troubleshooting utility server started on port {port}.")
        else:
            log.error(
                "Troubleshooting utility handler not specified. Will not start the server."
            )

    def start(self):
        """
        Starts the server.
        """
        self._thread.start()

    def stop(self):
        """
        Stops the server.
        """
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()
