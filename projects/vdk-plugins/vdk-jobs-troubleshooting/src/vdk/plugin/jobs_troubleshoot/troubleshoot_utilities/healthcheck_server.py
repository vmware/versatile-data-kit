# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from threading import Thread
from typing import Any


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
        else:
            self._server = HTTPServer(("", port), SimpleHTTPRequestHandler)
        self._thread = Thread(target=self._server.serve_forever)

    def __enter__(self):
        """
        Enters a with block. This method starts the server.
        """
        self.start()
        return self

    def __exit__(self, typ, value, traceback):
        """
        Exits a with block. This method stops the server.

        Parameters:
            typ (Any): The exception type.
            value (Any): The exception value.
            traceback (Any): The traceback.
        """
        self.stop()

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
