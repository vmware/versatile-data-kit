# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.job_input import IJobInput
from taurus.vdk.core import errors
from taurus.vdk.trino_utils import TrinoTemplateQueries

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

    Note: If there is no data in tmp_target_table, we are sure that the source table provided initially was empty,
    so we do nothing, target remains unchanged and we drop the empty tmp_target_table.
    """

    args = job_input.get_arguments()
    target_schema = args.get("target_schema")
    source_view = args.get("source_view")
    target_table = args.get("target_table")
    tmp_target_table = "tmp_" + target_table
    trino_queries = TrinoTemplateQueries(job_input)

    log.debug("Check if tmp target has data.")
    res = job_input.execute_query(
        f"""
        SELECT COUNT(*) FROM {target_schema}.{tmp_target_table}
        """
    )
    if res and res[0][0] > 0:
        log.debug(
            "Confirmed that tmp target has data, proceed with moving it to target."
        )
        trino_queries.perform_safe_move_data_to_table_step(
            from_db=target_schema,
            from_table_name=tmp_target_table,
            to_db=target_schema,
            to_table_name=target_table,
        )
    else:
        log.info(
            f"Target table {target_schema}.{target_table} remains unchanged "
            f"because source table {target_schema}.{source_view} was empty."
        )
        trino_queries.drop_table(target_schema, tmp_target_table)
