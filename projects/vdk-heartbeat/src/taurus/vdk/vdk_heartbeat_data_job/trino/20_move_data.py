# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):

    job_input.execute_query(
        """
    INSERT INTO {db}.{table_destination}
    SELECT uuid, 'python', hostname, pa__arrival_ts
    FROM {db}.{table_source}"""
    )

    result = job_input.execute_query(
        "SELECT uuid,hostname, pa__arrival_ts FROM {db}.{table_source}"
    )

    log.info(f"source data: {result}")

    # fake load test for now
    job_input.execute_query(
        """
    INSERT INTO {db}.{table_destination}
    SELECT uuid, 'load', hostname, pa__arrival_ts
    FROM {db}.{table_source}"""
    )

    # if result:  # Don't load an empty parquet file when table_source is empty.
    #     db = job_input.get_property('db')
    #     table = job_input.get_property('table_load_destination')
    #     job_input.load(result, f"{db}.{table}")
