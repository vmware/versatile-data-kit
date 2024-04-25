# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    payload_with_types = {
        "id": 5,
        "str_data": "string",
        "int_data": 12,
        "float_data": 1.2,
        "bool_data": True,
        "timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        "decimal_data": Decimal(0.1),
    }
    # print("\n\n\n\n\n")
    job_input.execute_query(
        sql="begin\n\texecute immediate 'drop table oracle_ingest';\n\texception when others then if sqlcode <> -942 then raise; end if;\nend;",
        database="oracle_one",
    )
    job_input.execute_query(
        sql="create table oracle_ingest (id number,str_data varchar2(255),int_data number,float_data float,bool_data number(1),timestamp_data timestamp,decimal_data decimal(14,8),primary key(id))",
        database="oracle_one",
    )
    job_input.send_object_for_ingestion(
        payload=payload_with_types,
        destination_table="oracle_ingest",
        method="oracle_one",
        target="oracle_one",
    )
