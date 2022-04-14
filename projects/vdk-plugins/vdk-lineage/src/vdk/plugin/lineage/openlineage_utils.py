# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid
from datetime import datetime
from typing import Optional

import attr
from openlineage.client.client import OpenLineageClient
from openlineage.client.client import OpenLineageClientOptions
from openlineage.client.facet import BaseFacet
from openlineage.client.facet import ParentRunFacet
from openlineage.client.facet import SCHEMA_URI
from openlineage.client.facet import SqlJobFacet
from openlineage.client.run import Dataset
from openlineage.client.run import Job
from openlineage.client.run import Run
from openlineage.client.run import RunEvent
from openlineage.client.run import RunState
from vdk.plugin.lineage import sql_lineage_parser

PRODUCER = "https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-lineage"


@attr.s
class VdkJobFacet(BaseFacet):
    op_id: str = attr.ib()
    execution_id: str = attr.ib()
    source_version: str = attr.ib()
    team: str = attr.ib()

    @staticmethod
    def _get_schema() -> str:
        return SCHEMA_URI + "#/definitions/VdkJobFacet"


def setup_client(url: str, api_key: str = None) -> Optional[OpenLineageClient]:
    if not url:
        return None
    return OpenLineageClient(url=url, options=OpenLineageClientOptions(api_key=api_key))


def run_event(
    state: RunState,
    job_name: str,
    job_namespace: str,
    run_id: str = str(uuid.uuid4()),
    parent: Optional[ParentRunFacet] = None,
    run_details: Optional[VdkJobFacet] = None,
) -> RunEvent:
    return RunEvent(
        eventType=state,
        eventTime=datetime.now().isoformat(),
        run=Run(runId=run_id, facets={"parent": parent} if parent else {}),
        job=Job(
            namespace=parent if parent else job_namespace,
            name=job_name,
            facets={"details": run_details} if run_details else {},
        ),
        producer=PRODUCER,
    )


def sql_event(
    state: RunState,
    sql: str,
    job_namespace: str,
    run_id: str,
    parent: Optional[ParentRunFacet] = None,
):
    lineage_data = sql_lineage_parser.get_table_lineage_from_query(sql, None, None)
    inputs = [Dataset(job_namespace, str(t)) for t in lineage_data.input_tables]
    outputs = (
        [Dataset(job_namespace, str(lineage_data.output_table))]
        if lineage_data.output_table
        else []
    )

    return RunEvent(
        eventType=state,
        eventTime=datetime.now().isoformat(),
        run=Run(runId=run_id, facets={"parent": parent} if parent else {}),
        job=Job(
            namespace=job_namespace,
            name=f"{parent.job['name']}",
            facets={"sql": SqlJobFacet(sql)},
        ),
        inputs=inputs,
        outputs=outputs,
        producer=PRODUCER,
    )
