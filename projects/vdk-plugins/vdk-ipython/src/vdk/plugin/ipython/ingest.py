# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import warnings

from IPython import get_ipython
from vdk.api.job_input import IJobInput
from vdk.plugin.ipython import job
from vdk.plugin.ipython.common import show_ipython_error
from vdk.plugin.ipython.job import JobControl

log = logging.getLogger(__name__)


def vdkingest(line, cell):
    """
    TOML based ingestion configuration
    """

    vdk: JobControl = get_ipython().user_global_ns.get("VDK", None)
    if not vdk:
        log.warning(
            "VDK is not initialized with '%reload_VDK'. "
            "Will auto-initialize now wth default parameters."
        )
        job.load_job()
        vdk = get_ipython().user_global_ns.get("VDK", None)
        if not vdk:
            message = "VDK cannot initialized. Please execute: %reload_VDK"
            show_ipython_error(message)
            return None

    job_input: IJobInput = vdk.get_initialized_job_input()

    try:
        from vdk.plugin.data_sources.mapping.data_flow import DataFlowInput
    except ImportError:
        raise ImportError(
            "vdk-data-sources is not installed. %%vdkingest is not available without it"
        )

    from vdk.plugin.data_sources.mapping import toml_parser
    import toml

    parsed_toml = toml.loads(cell)
    definitions = toml_parser.definitions_from_dict(parsed_toml)

    with DataFlowInput(job_input) as flow_input:
        flow_input.start_flows(definitions)
