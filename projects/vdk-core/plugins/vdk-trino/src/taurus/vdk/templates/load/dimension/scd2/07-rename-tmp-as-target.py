# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.job_input import IJobInput
from taurus.vdk.core import errors
from taurus.vdk.trino_utils import TrinoQueries

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    In this step we try to rename tmp_target_table (where we populated the result data in the previous step) to
    target table in the following way:
    1. Rename target_table to backup_target_table
    2. Try to rename tmp_target_table to target_table
    3. If 2 fails, try to restore target from backup
    4. If 3 succeeds, drop tmp target. The job fails.
    5. If 3 fails, target table is lost, its content are in backup_target_table. Next job retry will try to
    recover target on its first step.
    6. If 2 succeeds, drop backup, we are ready.
    """

    args = job_input.get_arguments()
    target_schema = args.get("target_schema")
    target_table = args.get("target_table")
    tmp_target_table = "tmp_" + target_table
    backup_target_table = "backup_" + target_table

    trino_queries = TrinoQueries(job_input)

    log.debug("Create backup from target")
    trino_queries.move_data_to_table(
        from_db=target_schema,
        from_table_name=target_table,
        to_db=target_schema,
        to_table_name=backup_target_table,
    )
    try:
        log.debug("Create target from tmp target")
        result = trino_queries.move_data_to_table(
            from_db=target_schema,
            from_table_name=tmp_target_table,
            to_db=target_schema,
            to_table_name=target_table,
        )
    except Exception as e:
        result = None
        if _try_recover_target_from_backup(
            trino_queries, target_schema, target_table, backup_target_table
        ):
            trino_queries.drop_table(target_schema, tmp_target_table)
            raise
        else:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.PLATFORM_ERROR,
                log=log,
                what_happened=f"""Recovering target from backup table failed. "
                "Table {target_schema}.{target_table} is lost!""",
                why_it_happened=f"""Step with renaming tmp table to target table failed, so recovery from backup was"
                                        "initiated, but it also failed with error: {e}""",
                consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail.",
                countermeasures=f"""Please, try the steps bellow in the following order:\n"
                "1. Try to rerun the data job OR\n"
                "2. First try to recover {target_schema}.{target_table} from"
                "{target_schema}.backup_{target_table} by manually executing:\n"
                "CREATE TABLE {target_schema}.{target_table} (LIKE {target_schema}.backup_{target_table})\n"
                "INSERT INTO {target_schema}.{target_table} SELECT * FROM {target_schema}.backup_{target_table}\n"
                "Then try to rerun the data job OR\n"
                "3. Report the issue to support team.""",
            )
    if result:
        log.debug("Target table was successfully created, and we can drop backup")
        trino_queries.drop_table(target_schema, backup_target_table)


def _try_recover_target_from_backup(
    trino_queries: TrinoQueries, db: str, target_table: str, backup_table: str
):
    log.debug("Try to recover target from backup")
    try:
        result = trino_queries.move_data_to_table(
            from_db=db,
            from_table_name=backup_table,
            to_db=db,
            to_table_name=target_table,
        )
    except Exception as e:
        result = None
        pass

    return result
