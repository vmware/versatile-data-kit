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
          `cluster_count` BIGINT
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT INTO TABLE `{target_schema}`.`{target_table}` VALUES (
          ("sddc01-r01", 1, "2019-11-18", 5 , 1),
          ("sddc02-r01", 2, "2019-11-18", 4 , 1)
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
          `cluster_count` BIGINT
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT INTO TABLE `{source_schema}`.`{source_view}` VALUES (
<<<<<<< HEAD
          ("sddc01-r01", 1, "2019-11-19", 5 , 1),
=======
          ("sddc01-r01", 1, "2019-11-19", 5 , 1),
>>>>>>> 1facbaee0ad94f2767c00404848ff0c88b0e2667
          ("sddc02-r01", 2, "2019-11-19", 4 , 1)
        )
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
          `cluster_count` BIGINT
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT INTO TABLE `{expect_schema}`.`{expect_table}` VALUES (
          ("sddc01-r01", 1, "2019-11-18", 5 , 1),
          ("sddc02-r01", 2, "2019-11-18", 4 , 1),
<<<<<<< HEAD
          ("sddc01-r01", 1, "2019-11-19", 5 , 1),
=======
          ("sddc01-r01", 1, "2019-11-19", 5 , 1),
>>>>>>> 1facbaee0ad94f2767c00404848ff0c88b0e2667
          ("sddc02-r01", 2, "2019-11-19", 4 , 1)
        )
    """
    )
