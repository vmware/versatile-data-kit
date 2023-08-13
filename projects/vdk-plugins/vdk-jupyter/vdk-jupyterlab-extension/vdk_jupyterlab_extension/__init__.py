# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import tornado
from jupyterlab.labapp import LabApp

from ._version import __version__
from .config import VdkJupyterConfig
from .handlers import setup_handlers

log = logging.getLogger(__name__)


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "vdk-jupyterlab-extension"}]


def _jupyter_server_extension_points():
    return [{"module": "vdk_jupyterlab_extension"}]


def _load_jupyter_server_extension(server_app: LabApp):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    tornado.log.enable_pretty_logging()
    tornado.log.app_log.setLevel(tornado.log.logging.DEBUG)

    vdk_config = VdkJupyterConfig(config=server_app.config)
    log.info(f"VDK Jupyter config: {vdk_config.config}")
    log.info(
        f"VDK Jupyter oauth2_authorization_url: {vdk_config.oauth2_authorization_url}"
    )
    log.info(f"app config: {server_app.config}")

    setup_handlers(server_app.web_app, vdk_config)
    name = "vdk_jupyterlab_extension"
    server_app.log.info(f"Registered {name} server extension")


# For backward compatibility with notebook server - useful for Binder/JupyterHub
load_jupyter_server_extension = _load_jupyter_server_extension
