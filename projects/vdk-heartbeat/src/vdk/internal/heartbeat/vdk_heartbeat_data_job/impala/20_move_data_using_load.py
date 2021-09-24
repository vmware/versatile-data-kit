# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vacloud.api.job_input import IJobInput

# TODO: migrate to vdk.api

log = logging.getLogger(__name__)


def run(job_input: IJobInput):

    job_input.execute_query("REFRESH {db}.{table_source}")

    job_input.execute_query(
        """
    INSERT INTO TABLE {db}.{table_destination} PARTITION (pa__arrival_ts)
    SELECT uuid, 'python', hostname, pa__arrival_ts
    FROM {db}.{table_source};"""
    )

    result = job_input.execute_query(
        "SELECT uuid,hostname, pa__arrival_ts FROM {db}.{table_source}"
    )

    log.info(f"source data: {result}")

    if result:  # Don't load an empty parquet file when table_source is empty.
        db = job_input.get_property("db")
        table = job_input.get_property("table_load_destination")
        job_input.load(result, f"{db}.{table}")
