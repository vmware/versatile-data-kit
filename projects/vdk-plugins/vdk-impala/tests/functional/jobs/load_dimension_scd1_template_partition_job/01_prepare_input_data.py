# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Load example input data for an scd1 template test.
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
          `org_id` INT,
          `org_name` STRING,
          `sddc_limit` INT,
          `org_host_limit` INT
        )
        PARTITIONED BY (`org_type` STRING, `company_name` STRING)
        STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        TRUNCATE `{target_schema}`.`{target_table}`
    """
    )
    # Step 2: create a table that represents the next state

    # job_input.execute_query(u'''
    #     DROP TABLE IF EXISTS `{source_schema}`.`{source_view}`
    # ''')
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{source_schema}`.`{source_view}` (
          `org_id` INT,
          `org_name` STRING,
          `sddc_limit` INT,
          `org_host_limit` INT,
          `org_type` STRING,
          `company_name` STRING
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{source_schema}`.`{source_view}` VALUES (
          (1, "mullen@actual.com"        , 2, 32, "CUSTOMER_MSP_TENANT", "actual Master Org"),
          (2, "johnlocke@vmware.com"     , 1, 6 , "CUSTOMER_POC"       , "VMware"           ),
          (3, "lilly.johnsonn@goofys.com", 2, 32, "CUSTOMER"           , "Goofy"            ),
          (4, "jilliandoe@uncanny.ca"    , 2, 32, "PARTNER_SISO"       , "Uncanny Company"  ),
          (5, "jane.doe@vmware.com"      , 2, 32, "CUSTOMER"           , "VMware"           ),
          (6, "john.doe@pharmamed.com"   , 2, 32, "CUSTOMER"           , "PharmaMed"        ),
          (7, "andrej.maya@acme.com"     , 2, 32, "PARTNER_SISO"       , "ACME"             ),
          (8, "guang@vmware.com"         , 2, 32, "INTERNAL_CORE"      , "VMware"           )
        )
    """
    )
