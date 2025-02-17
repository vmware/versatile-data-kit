# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput) -> None:
    # Step 1: create a table that represents the current state

    job_input.execute_query(
        """
        DROP TABLE IF EXISTS {target_schema}.{target_table}
    """
    )
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS {target_schema}.{target_table} (
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
        """
        INSERT INTO {target_schema}.{target_table} VALUES
              (2, 'johnlocke@vmware.com'     , 'CUSTOMER_POC'       , 'VMware'           , 1, 6 ),
              (3, 'lilly.johnsonn@goofys.com', 'CUSTOMER'           , 'Goofy''s'         , 2, 16),
              (4, 'jilliandoe@uncanny.ca'    , 'PARTNER_SISO'       , 'Uncanny Company'  , 2, 16),
              (5, 'jane.doe@vmware.com'      , 'CUSTOMER'           , 'VMware'           , 2, 32),
              (6, 'john.doe@pharmamed.com'   , 'CUSTOMER'           , 'PharmaMed'        , 1, 32),
              (7, 'andrej.maya@acme.com'     , 'PARTNER_SISO'       , 'ACME'             , 1, 32),
              (8, 'guang@vmware.com'         , 'INTERNAL_CORE'      , 'VMware'           , 4, 32)
    """
    )

    # Step 2: create a table that represents the data that will be upserted

    job_input.execute_query(
        """
        DROP TABLE IF EXISTS {source_schema}.{source_view}
    """
    )
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS {source_schema}.{source_view} (
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
        """INSERT  INTO {source_schema}.{source_view} VALUES
              (7,  'andrej.maya@acme.com'      , 'CUSTOMER'      , 'ACME'        , 1, 32),
              (8,  'guang@vmware.com'          , 'CUSTOMER'      , 'VMware'      , 4, 32),
              (9,  'johnlocke@vmware.com'      , 'CUSTOMER_POC'  , 'VMware'      , 1, 6 ),
              (10, 'lilly.johnsonn@goofys.com' , 'CUSTOMER'      , 'Goofy''s'    , 2, 16)
          """
    )

    # Step 3: Create a table containing the state expected after upserting the target table with the source table data

    job_input.execute_query(
        """
        DROP TABLE IF EXISTS {expect_schema}.{expect_table}
    """
    )
    job_input.execute_query(
        """
        CREATE TABLE IF NOT EXISTS {expect_schema}.{expect_table} (
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
        """
        INSERT INTO {expect_schema}.{expect_table} VALUES
              (2,  'johnlocke@vmware.com'     , 'CUSTOMER_POC'   , 'VMware'           , 1, 6 ),
              (3,  'lilly.johnsonn@goofys.com', 'CUSTOMER'       , 'Goofy''s'         , 2, 16),
              (4,  'jilliandoe@uncanny.ca'    , 'PARTNER_SISO'   , 'Uncanny Company'  , 2, 16),
              (5,  'jane.doe@vmware.com'      , 'CUSTOMER'       , 'VMware'           , 2, 32),
              (6,  'john.doe@pharmamed.com'   , 'CUSTOMER'       , 'PharmaMed'        , 1, 32),
              (7,  'andrej.maya@acme.com'     , 'CUSTOMER'       , 'ACME'             , 1, 32),
              (8,  'guang@vmware.com'         , 'CUSTOMER'       , 'VMware'           , 4, 32),
              (9,  'johnlocke@vmware.com'     , 'CUSTOMER_POC'   , 'VMware'           , 1, 6 ),
              (10, 'lilly.johnsonn@goofys.com', 'CUSTOMER'       , 'Goofy''s'         , 2, 16)
    """
    )
