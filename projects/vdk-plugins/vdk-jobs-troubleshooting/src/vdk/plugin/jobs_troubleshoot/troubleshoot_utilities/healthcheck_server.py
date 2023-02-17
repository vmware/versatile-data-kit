# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import socket
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
        try:
            if handler:
                port = self.find_open_port(port)
                self._server = HTTPServer(("", port), handler)
                self._thread = Thread(
                    target=self._server.serve_forever,
                    name="troubleshooting_utility",
                    daemon=True,
                )
                log.info(f"Troubleshooting utility server will start on port {port}.")
            else:
                log.error(
                    "Troubleshooting utility handler not specified. Will not start the server."
                )
        except Exception as e:
            logging.error(
                "Error during troubleshooting server initialization", exc_info=e
            )

    def start(self):
        """
        Starts the server.
        """
        try:
            self._thread.start()
            logging.info("Troubleshooting utility server started.")
        except Exception as e:
            logging.error("Unable to start troubleshooting server", exc_info=e)

    def stop(self):
        """
        Stops the server.
        """
        try:
            self._server.shutdown()
            self._server.server_close()
            logging.info("Troubleshooting utility server stopped.")
        except Exception as e:
            logging.error("Unable to stop troubleshooting server", exc_info=e)

    @staticmethod
    def find_open_port(start_port: int):
        port = start_port
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(("", port))
                s.close()
                return port
            except OSError:
                # Port is already in use. Try the next one
                port += 1
