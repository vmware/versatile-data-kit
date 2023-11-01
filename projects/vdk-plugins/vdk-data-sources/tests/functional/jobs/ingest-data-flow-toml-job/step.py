# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os

from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.mapping import toml_parser
from vdk.plugin.data_sources.mapping.data_flow import DataFlowInput


def run(job_input: IJobInput):
    with DataFlowInput(job_input) as flow_input:
        flow_input.start_flows(
            toml_parser.load_config(
                os.path.join(job_input.get_job_directory(), "ingest.toml")
            )
        )
