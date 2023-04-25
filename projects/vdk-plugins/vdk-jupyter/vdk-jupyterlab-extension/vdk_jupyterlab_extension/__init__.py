# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from ._version import __version__
from .handlers import setup_handlers


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "vdk-jupyterlab-extension"}]


def _jupyter_server_extension_points():
    return [{"module": "vdk_jupyterlab_extension"}]


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_handlers(server_app.web_app)
    name = "vdk_jupyterlab_extension"
    server_app.log.info(f"Registered {name} server extension")


# For backward compatibility with notebook server - useful for Binder/JupyterHub
load_jupyter_server_extension = _load_jupyter_server_extension
