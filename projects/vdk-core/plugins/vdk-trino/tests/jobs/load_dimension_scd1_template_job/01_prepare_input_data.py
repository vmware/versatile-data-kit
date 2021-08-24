# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Load example input data for an scd1 template test.
"""
from taurus.api.job_input import IJobInput


def run(job_input: IJobInput) -> None:
    target_schema = job_input.get_arguments().get("target_schema")
    target_table = job_input.get_arguments().get("target_table")
    source_schema = job_input.get_arguments().get("source_schema")
    source_view = job_input.get_arguments().get("source_view")

    # Step 1: create a new table that represents the current state
    job_input.execute_query(
        f"""
            DROP TABLE IF EXISTS "{target_schema}"."{target_table}"
        """
    )
    job_input.execute_query(
        f"""
            CREATE TABLE IF NOT EXISTS "{target_schema}"."{target_table}" (
              org_id INT,
              org_name VARCHAR,
              org_type VARCHAR,
              company_name VARCHAR,
              sddc_limit INT,
              org_host_limit INT
            )
        """
    )
    job_input.execute_query(
        f"""
            INSERT INTO "{target_schema}"."{target_table}" VALUES
              (2, 'johnlocke@vmware.com'     , 'CUSTOMER_POC'       , 'VMware'           , 1, 6 ),
              (3, 'lilly.johnsonn@goofys.com', 'CUSTOMER'           , 'Goofy''s'          , 2, 16),
              (4, 'jilliandoe@uncanny.ca'    , 'PARTNER_SISO'       , 'Uncanny Company'  , 2, 16),
              (5, 'jane.doe@vmware.com'      , 'CUSTOMER'           , 'VMware'           , 2, 32),
              (6, 'john.doe@pharmamed.com'   , 'CUSTOMER'           , 'PharmaMed'        , 1, 32),
              (7, 'andrej.maya@acme.com'     , 'PARTNER_SISO'       , 'ACME'             , 1, 32),
              (8, 'guang@vmware.com'         , 'INTERNAL_CORE'      , 'VMware'           , 4, 32)
        """
    )

    # Step 2: create a new table that represents the next state
    job_input.execute_query(
        f"""
               DROP TABLE IF EXISTS "{source_schema}"."{source_view}"
           """
    )
    job_input.execute_query(
        f"""
            CREATE TABLE IF NOT EXISTS "{source_schema}"."{source_view}" (
              org_id INT,
              org_name VARCHAR,
              org_type VARCHAR,
              company_name VARCHAR,
              sddc_limit INT,
              org_host_limit INT
            )
        """
    )
    job_input.execute_query(
        f"""
            INSERT INTO "{source_schema}"."{source_view}" VALUES
              (1, 'mullen@actual.com'        , 'CUSTOMER_MSP_TENANT', 'actual Master Org', 2, 32),
              (2, 'johnlocke@vmware.com'     , 'CUSTOMER_POC'       , 'VMware'           , 1, 6 ),
              (3, 'lilly.johnsonn@goofys.com', 'CUSTOMER'           , 'Goofy''s'          , 2, 32),
              (4, 'jilliandoe@uncanny.ca'    , 'PARTNER_SISO'       , 'Uncanny Company'  , 2, 32),
              (5, 'jane.doe@vmware.com'      , 'CUSTOMER'           , 'VMware'           , 2, 32),
              (6, 'john.doe@pharmamed.com'   , 'CUSTOMER'           , 'PharmaMed'        , 2, 32),
              (7, 'andrej.maya@acme.com'     , 'PARTNER_SISO'       , 'ACME'             , 2, 32),
              (8, 'guang@vmware.com'         , 'INTERNAL_CORE'      , 'VMware'           , 2, 32)
        """
    )
