# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.job_input import IJobInput
from taurus.vdk.core import errors
from taurus.vdk.trino_utils import TrinoQueries

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    In this step we try to recover unexistent target table from backup.
    In some cases the template might fail during the step where new data is written in target table
    (last step where tmp_target_table is renamed to target_table). If this happens, the job fails and
    target table is no longer present. Fortunately it has a backup (backup_target_table).
    So when the job is retried, this first step should recover the target (if the reason for the previous fail
    is no longer present).
    """

    args = job_input.get_arguments()
    target_schema = args.get("target_schema")
    target_table = args.get("target_table")
    tmp_target_table = "tmp_" + target_table
    backup_target_table = "backup_" + target_table

    trino_queries = TrinoQueries(job_input)

    if not trino_queries.table_exists(target_schema, target_table):
        log.debug("If there is backup, try to recover target from it")
        if trino_queries.table_exists(target_schema, backup_target_table):
            log.debug("Try to recover target from backup")
            try:
                trino_queries.move_data_to_table(
                    target_schema, backup_target_table, target_schema, target_table
                )
                log.info(
                    f"""Successfully recovered {target_schema}.{target_table} from "
                    "{target_schema}.{backup_target_table}"""
                )
            except Exception as e:
                errors.log_and_throw(
                    to_be_fixed_by=errors.ResolvableBy.PLATFORM_ERROR,
                    log=log,
                    what_happened=f"Target table is unexistent and recovering it from backup table failed with "
                    f"exception: {e}",
                    why_it_happened=f"""One of the previous job retries failed after dropping "
                    "{target_schema}.{target_table} and before renaming "
                    "{target_schema}.{tmp_target_table} to "
                    "{target_schema}.{target_table}.""",
                    consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail.",
                    countermeasures="You could try to recover {target_schema}.{target_table} from"
                    "{target_schema}.{backup_target_table} by hand and then "
                    "rerun the job."
                    "",
                )

        # if there is no target and no backup, the user provided invalid target table
        # TODO: create target table automatically if not provided by user
        else:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=log,
                what_happened="Cannot find target table",
                why_it_happened=f"Template is called for unexistent target table: {target_schema}.{target_table}",
                consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail.",
                countermeasures="Provide valid target table arguments.",
            )
