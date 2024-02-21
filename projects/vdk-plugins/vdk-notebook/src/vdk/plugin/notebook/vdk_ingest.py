# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


TYPE_INGEST = "ingest"


def run_ingest_step(step: "NotebookCellStep", job_input: IJobInput) -> bool:
    """
    Run ingest data flow step. Only if vdk-data-sources is installed.
    """
    try:
        from vdk.plugin.data_sources.mapping.data_flow import DataFlowInput
        from vdk.plugin.data_sources.mapping import toml_parser
    except ImportError:
        raise ImportError(
            "vdk-data-sources is not installed. ingestion step is not available without it"
        )

    import toml

    parsed_toml = toml.loads(step.source)
    definitions = toml_parser.definitions_from_dict(parsed_toml)

    with DataFlowInput(job_input) as flow_input:
        flow_input.start_flows(definitions)
