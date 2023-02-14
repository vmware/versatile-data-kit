# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Load example input data for an scd2 template test.
"""
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
          `{sk_column}` STRING,
          `{active_from_column}` TIMESTAMP,
          `{active_to_column}` TIMESTAMP,
          `{id_column}` INT,
          `updated_by_user_id` INT,
          `state` STRING,
          `is_nsxt` BOOLEAN,
          `cloud_vendor` STRING,
          `version` SMALLINT
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{target_schema}`.`{target_table}` VALUES (
          ("sddc01-v01", "2019-01-01", "9999-12-31", 1, 7, "RUNNING"     , false, 'Azure', 498),
          ("sddc02-v01", "2019-02-01", "9999-12-31", 2, 9, "STOPPED"     , false, 'AWS'  , 500),
          ("sddc03-v01", "2019-03-01", "9999-12-31", 3, 3, "PROVISIONING", false, 'Azure', 497),
          ("sddc04-v01", "2019-04-01", "9999-12-31", 4, 5, "PROVISIONING", true , 'Azure', 498),
          ("sddc05-v01", "2019-05-01", "2019-05-02", 5, 9, "STARTING"    , true , 'AWS'  , 500),
          ("sddc05-v02", "2019-05-02", "2019-05-03", 5, 2, "STARTING"    , true , 'AWS'  , 500),
          ("sddc05-v03", "2019-05-03", "9999-12-31", 5, 3, "STARTING"    , true , 'AWS'  , 500)
        )
    """
    )

    # Step 2: create a table that represents the delta to be applied

    # job_input.execute_query(u'''
    #     DROP TABLE IF EXISTS `{source_schema}`.`{source_view}`
    # ''')
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{source_schema}`.`{source_view}` (
          `{updated_at_column}` TIMESTAMP,
          `{id_column}` INT,
          `updated_by_user_id` INT,
          `state` STRING,
          `is_nsxt` BOOLEAN,
          `cloud_vendor` STRING,
          `version` SMALLINT
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{source_schema}`.`{source_view}` VALUES (
          ("2019-02-02", 2, 1, "STARTING"    , false, 'AWS'  , 500), -- Update (1) - new  time, new  values
          ("2019-03-01", 3, 4, "RUNNING"     , false, 'Azure', 497), -- Update (2) - same time, new  values
          ("2019-04-02", 4, 5, "PROVISIONING", true , 'Azure', 498), -- Update (3) - new  time, same values
          ("2019-05-01", 5, 9, "STARTING"    , true , 'AWS'  , 500), -- Update (4) - same time, same values
          ("2019-05-02", 5, 9, "STARTING"    , true , 'AWS'  , 500), -- Update (5) - same time, prev values
          ("2019-05-04", 5, 9, "STARTING"    , true , 'AWS'  , 500), -- Update (1) - new  time, new  values
          ("2019-06-01", 6, 9, "STARTING"    , true , 'AWS'  , 499)  -- Insert
        )
    """
    )

    # Step 3: Create a table containing the state expected after updating the current state with the given delta

    # job_input.execute_query(u'''
    #     DROP TABLE IF EXISTS `{expect_schema}`.`{expect_table}`
    # ''')
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{expect_schema}`.`{expect_table}` (
          `{sk_column}` STRING,
          `{active_from_column}` TIMESTAMP,
          `{active_to_column}` TIMESTAMP,
          `{id_column}` INT,
          `updated_by_user_id` INT,
          `state` STRING,
          `is_nsxt` BOOLEAN,
          `cloud_vendor` STRING,
          `version` SMALLINT
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{expect_schema}`.`{expect_table}` VALUES (
          ("sddc01-v01", "2019-01-01", "9999-12-31", 1, 7, "RUNNING"     , false, 'Azure', 498),

          ("sddc02-v01", "2019-02-01", "2019-02-02", 2, 9, "STOPPED"     , false, 'AWS'  , 500),
          ("sddc02-v02", "2019-02-02", "9999-12-31", 2, 1, "STARTING"    , false, 'AWS'  , 500),

          ("sddc03-v01", "2019-03-01", "9999-12-31", 3, 4, "RUNNING"     , false, 'Azure', 497),

          ("sddc04-v01", "2019-04-01", "9999-12-31", 4, 5, "PROVISIONING", true , 'Azure', 498),

          ("sddc05-v01", "2019-05-01", "2019-05-03", 5, 9, "STARTING"    , true , 'AWS'  , 500),
          ("sddc05-v03", "2019-05-03", "2019-05-04", 5, 3, "STARTING"    , true , 'AWS'  , 500),
          ("sddc05-v04", "2019-05-04", "9999-12-31", 5, 9, "STARTING"    , true , 'AWS'  , 500),

          ("sddc06-v01", "2019-06-01", "9999-12-31", 6, 9, "STARTING"    , true , 'AWS'  , 499)
        )
    """
    )
