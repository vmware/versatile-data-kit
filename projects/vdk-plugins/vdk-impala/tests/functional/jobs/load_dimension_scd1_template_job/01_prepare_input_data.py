# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
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

    # job_input.execute_query(u"""
    #     CREATE DATABASE IF NOT EXISTS `{target_schema}`
    # """)

    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `{target_schema}`.`{target_table}` (
          `org_id` INT,
          `org_name` STRING,
          `org_type` STRING,
          `company_name` STRING,
          `sddc_limit` INT,
          `org_host_limit` INT
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{target_schema}`.`{target_table}` VALUES (
          (2, "johnlocke@vmware.com"     , "CUSTOMER_POC"       , "VMware"           , 1, 6 ),
          (3, "lilly.johnsonn@goofys.com", "CUSTOMER"           , "Goofy's"          , 2, 16),
          (4, "jilliandoe@uncanny.ca"    , "PARTNER_SISO"       , "Uncanny Company"  , 2, 16),
          (5, "jane.doe@vmware.com"      , "CUSTOMER"           , "VMware"           , 2, 32),
          (6, "john.doe@pharmamed.com"   , "CUSTOMER"           , "PharmaMed"        , 1, 32),
          (7, "andrej.maya@acme.com"     , "PARTNER_SISO"       , "ACME"             , 1, 32),
          (8, "guang@vmware.com"         , "INTERNAL_CORE"      , "VMware"           , 4, 32)
        )
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
          `org_type` STRING,
          `company_name` STRING,
          `sddc_limit` INT,
          `org_host_limit` INT
        ) STORED AS PARQUET
    """
    )
    job_input.execute_query(
        """
        INSERT OVERWRITE TABLE `{source_schema}`.`{source_view}` VALUES (
          (1, "mullen@actual.com"        , "CUSTOMER_MSP_TENANT", "actual Master Org", 2, 32),
          (2, "johnlocke@vmware.com"     , "CUSTOMER_POC"       , "VMware"           , 1, 6 ),
          (3, "lilly.johnsonn@goofys.com", "CUSTOMER"           , "Goofy's"          , 2, 32),
          (4, "jilliandoe@uncanny.ca"    , "PARTNER_SISO"       , "Uncanny Company"  , 2, 32),
          (5, "jane.doe@vmware.com"      , "CUSTOMER"           , "VMware"           , 2, 32),
          (6, "john.doe@pharmamed.com"   , "CUSTOMER"           , "PharmaMed"        , 2, 32),
          (7, "andrej.maya@acme.com"     , "PARTNER_SISO"       , "ACME"             , 2, 32),
          (8, "guang@vmware.com"         , "INTERNAL_CORE"      , "VMware"           , 2, 32)
        )
    """
    )
