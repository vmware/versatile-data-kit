# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import tempfile

from vdk.api.job_input import IJobInput
from vdk.plugin.dag.dag_runner import DagInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Dummy arguments {job_input.get_arguments()}")
    with tempfile.NamedTemporaryFile(prefix="temp-", mode="w+") as temp_file:
        job1 = dict(
            job_name="write-file-job",
            depends_on=[],
            arguments=dict(path=temp_file.name),
        )
        job2 = dict(
            job_name="fail-job", depends_on=["write-file-job"], fail_dag_on_error=False
        )
        job3 = dict(
            job_name="read-file-job",
            depends_on=["write-file-job"],
            arguments=dict(path=temp_file.name),
        )
        DagInput().run_dag([job1, job2, job3])
