# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.job_input import IJobInput
from taurus.vdk.core import errors
from taurus.vdk.trino_utils import TrinoTemplateQueries

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    In this step we try to recover potentially unexistent target table from backup.
    In some cases the template might fail during the step where new data is written in target table
    (last step where tmp_target_table contents are moved to target_table). If this happens, the job fails and
    target table is no longer present. Fortunately it has a backup.
    So when the job is retried, this first step should recover the target (if the reason for the previous fail
    is no longer present).
    """

    args = job_input.get_arguments()
    target_schema = args.get("target_schema")
    target_table = args.get("target_table")
    trino_queries = TrinoTemplateQueries(job_input)

    trino_queries.ensure_target_exists_step(db=target_schema, target_name=target_table)
