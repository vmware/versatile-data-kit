# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


__author__ = "VMware, Inc."
__copyright__ = (
    "Copyright 2019 VMware, Inc.  All rights reserved. -- VMware Confidential"
)


def run(job_input: IJobInput) -> None:
    # Step 1: create a table that represents the current state

    # job_input.execute_query(u'''
    #     DROP TABLE IF EXISTS `{target_schema}`.`{target_table}`
    # ''')
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{target_schema}`.`{target_table}` (
          `dim_sddc_sk` STRING,
          `dim_org_id` INT,
          `dim_date_id` TIMESTAMP,
          `host_count` BIGINT,
          `cluster_count` BIGINT,
          `{last_arrival_ts}` TIMESTAMP
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{target_schema}`.`{target_table}` VALUES (
          -- 2019-11-18
          ("sddc01-r01", 1, "2019-11-18", 5 , 1, "2019-11-18 09:00:00"),
          ("sddc02-r01", 2, "2019-11-18", 4 , 1, "2019-11-18 09:00:00"),
          ("sddc03-r01", 3, "2019-11-18", 12, 3, "2019-11-18 09:00:00"),
          ("sddc04-r01", 4, "2019-11-18", 4 , 1, "2019-11-18 09:00:00"),
          -- 2019-11-19
          ("sddc01-r01", 1, "2019-11-19", 5 , 1, "2019-11-19 09:00:00"),
          ("sddc02-r01", 2, "2019-11-19", 4 , 1, "2019-11-19 09:00:00"),
          ("sddc03-r01", 3, "2019-11-19", 13, 3, "2019-11-19 09:00:00"),
          ("sddc04-r01", 4, "2019-11-19", 3 , 1, "2019-11-19 09:00:00"),
          ("sddc05-r02", 5, "2019-11-19", 20, 4, "2019-11-19 09:00:00")
        )
    """
    )

    # Step 2: create a table that represents the next snapshot

    # job_input.execute_query(u'''
    #     DROP TABLE IF EXISTS `{source_schema}`.`{source_view}`
    # ''')
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{source_schema}`.`{source_view}` (
          `dim_sddc_sk` STRING,
          `dim_org_id` INT,
          `dim_date_id` TIMESTAMP,
          `host_count` BIGINT,
          `cluster_count` BIGINT,
          `{last_arrival_ts}` TIMESTAMP
        ) STORED AS PARQUET
    """
    )
    # We are testing the case when the next snapshot is empty
    job_input.execute_query(
        """
        TRUNCATE `{source_schema}`.`{source_view}`
    """
    )

    # Step 3: Create a table containing the state expected after updating the current state with the next snapshot

    # job_input.execute_query(u'''
    #     DROP TABLE IF EXISTS `{expect_schema}`.`{expect_table}`
    # ''')
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{expect_schema}`.`{expect_table}` (
          `dim_sddc_sk` STRING,
          `dim_org_id` INT,
          `dim_date_id` TIMESTAMP,
          `host_count` BIGINT,
          `cluster_count` BIGINT,
          `{last_arrival_ts}` TIMESTAMP
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{expect_schema}`.`{expect_table}` VALUES (
          -- 2019-11-18
          -- 2019-11-18
          ("sddc01-r01", 1, "2019-11-18", 5 , 1, "2019-11-18 09:00:00"),
          ("sddc02-r01", 2, "2019-11-18", 4 , 1, "2019-11-18 09:00:00"),
          ("sddc03-r01", 3, "2019-11-18", 12, 3, "2019-11-18 09:00:00"),
          ("sddc04-r01", 4, "2019-11-18", 4 , 1, "2019-11-18 09:00:00"),
          -- 2019-11-19
          ("sddc01-r01", 1, "2019-11-19", 5 , 1, "2019-11-19 09:00:00"),
          ("sddc02-r01", 2, "2019-11-19", 4 , 1, "2019-11-19 09:00:00"),
          ("sddc03-r01", 3, "2019-11-19", 13, 3, "2019-11-19 09:00:00"),
          ("sddc04-r01", 4, "2019-11-19", 3 , 1, "2019-11-19 09:00:00"),
          ("sddc05-r02", 5, "2019-11-19", 20, 4, "2019-11-19 09:00:00")
        )
    """
    )
