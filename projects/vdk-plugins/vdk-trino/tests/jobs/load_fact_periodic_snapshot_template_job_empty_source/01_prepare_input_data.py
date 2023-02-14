# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Load example input data for a periodic_snapshot template test with empty source.
"""
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput) -> None:
    # Step 1: create a table that represents the current state

    job_input.execute_query(
        """
        DROP TABLE IF EXISTS "{target_schema}"."{target_table}"
    """
    )
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS "{target_schema}"."{target_table}" (
          dim_sddc_sk VARCHAR,
          dim_org_id INT,
          dim_date_id TIMESTAMP,
          host_count BIGINT,
          cluster_count BIGINT,
          "{last_arrival_ts}" TIMESTAMP
        )
    """
    )
    job_input.execute_query(
        """
        INSERT INTO "{target_schema}"."{target_table}" VALUES
          -- 2019-11-18
          ('sddc01-r01', 1, TIMESTAMP '2019-11-18', 5 , 1, TIMESTAMP '2019-11-18 09:00:00'),
          ('sddc02-r01', 2, TIMESTAMP '2019-11-18', 4 , 1, TIMESTAMP '2019-11-18 09:00:00'),
          ('sddc03-r01', 3, TIMESTAMP '2019-11-18', 12, 3, TIMESTAMP '2019-11-18 09:00:00'),
          ('sddc04-r01', 4, TIMESTAMP '2019-11-18', 4 , 1, TIMESTAMP '2019-11-18 09:00:00'),
          -- 2019-11-19
          ('sddc01-r01', 1, TIMESTAMP '2019-11-19', 5 , 1, TIMESTAMP '2019-11-19 09:00:00'),
          ('sddc02-r01', 2, TIMESTAMP '2019-11-19', 4 , 1, TIMESTAMP '2019-11-19 09:00:00'),
          ('sddc03-r01', 3, TIMESTAMP '2019-11-19', 13, 3, TIMESTAMP '2019-11-19 09:00:00'),
          ('sddc04-r01', 4, TIMESTAMP '2019-11-19', 3 , 1, TIMESTAMP '2019-11-19 09:00:00'),
          ('sddc05-r02', 5, TIMESTAMP '2019-11-19', 20, 4, TIMESTAMP '2019-11-19 09:00:00')
    """
    )

    # Step 2: create a table that represents the next snapshot, empty in this case

    job_input.execute_query(
        """
        DROP TABLE IF EXISTS "{source_schema}"."{source_view}"
    """
    )
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS "{source_schema}"."{source_view}" (
          dim_sddc_sk VARCHAR,
          dim_org_id INT,
          dim_date_id TIMESTAMP,
          host_count BIGINT,
          cluster_count BIGINT,
          "{last_arrival_ts}" TIMESTAMP
        )
    """
    )

    # Step 3: Create a table containing the state expected after updating the current state with the next snapshot

    job_input.execute_query(
        """
        DROP TABLE IF EXISTS "{expect_schema}"."{expect_table}"
    """
    )
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS "{expect_schema}"."{expect_table}" (
          dim_sddc_sk VARCHAR,
          dim_org_id INT,
          dim_date_id TIMESTAMP,
          host_count BIGINT,
          cluster_count BIGINT,
          "{last_arrival_ts}" TIMESTAMP
        )
    """
    )
    job_input.execute_query(
        """
        INSERT INTO "{expect_schema}"."{expect_table}" VALUES
          -- 2019-11-18
          ('sddc01-r01', 1, TIMESTAMP '2019-11-18', 5 , 1, TIMESTAMP '2019-11-18 09:00:00'),
          ('sddc02-r01', 2, TIMESTAMP '2019-11-18', 4 , 1, TIMESTAMP '2019-11-18 09:00:00'),
          ('sddc03-r01', 3, TIMESTAMP '2019-11-18', 12, 3, TIMESTAMP '2019-11-18 09:00:00'),
          ('sddc04-r01', 4, TIMESTAMP '2019-11-18', 4 , 1, TIMESTAMP '2019-11-18 09:00:00'),
          -- 2019-11-19
          ('sddc01-r01', 1, TIMESTAMP '2019-11-19', 5 , 1, TIMESTAMP '2019-11-19 09:00:00'),
          ('sddc02-r01', 2, TIMESTAMP '2019-11-19', 4 , 1, TIMESTAMP '2019-11-19 09:00:00'),
          ('sddc03-r01', 3, TIMESTAMP '2019-11-19', 13, 3, TIMESTAMP '2019-11-19 09:00:00'),
          ('sddc04-r01', 4, TIMESTAMP '2019-11-19', 3 , 1, TIMESTAMP '2019-11-19 09:00:00'),
          ('sddc05-r02', 5, TIMESTAMP '2019-11-19', 20, 4, TIMESTAMP '2019-11-19 09:00:00')
    """
    )
