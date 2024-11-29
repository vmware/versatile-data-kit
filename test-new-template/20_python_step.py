# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Function named `run` is required in order for a python script to be recognized as a Data Job Python step and executed.

    VDK provides to every python step an object - job_input - that has methods for:

    * executing queries to OLAP Database;
    * ingesting data into a database;
    * processing data into a database.
    See IJobInput documentation for more details.
    """
    log.info(f"Starting job step {__name__}")

    def sample_check(random_table_name):
        return True

    # Write your python code inside here ... for example:
    job_input.execute_template(
        template_name='scd_upsert',
        template_args={
            'source_schema': 'starshot_internal_dw_stg',
            'source_view': 'sbuldeev_vw_template_test',
            'target_schema': 'starshot_internal_dw_stg',
            'target_table': 'sbuldeev_dw_template_test',
            'id_column': 'org_id',
            'check': sample_check
        },
        database="trino",
    )

    job_input.execute_query("SELECT 1")
