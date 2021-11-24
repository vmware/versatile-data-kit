# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput
from vdk.internal.core import errors
from vdk.plugin.trino.trino_utils import TrinoTemplateQueries

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    In this step we try to move data from tmp_target_table (where we populated the result data in the previous step)
    to target table in the following way:
    1. Move data from target_table to a backup table
    2. Try to move data from tmp_target_table to target_table
    3. If 2 fails, try to restore target from backup
    4. If 3 succeeds, drop tmp target. The job fails.
    5. If 3 fails, target table is lost, its content are in the backup table. Next job retry will try to
    recover target on its first step.
    6. If 2 succeeds, drop backup, we are ready.
    """

    args = job_input.get_arguments()
    target_schema = args.get("target_schema")
    target_table = args.get("target_table")
    tmp_target_table = "tmp_" + target_table
    trino_queries = TrinoTemplateQueries(job_input)

    trino_queries.perform_safe_move_data_to_table_step(
        from_db=target_schema,
        from_table_name=tmp_target_table,
        to_db=target_schema,
        to_table_name=target_table,
    )
