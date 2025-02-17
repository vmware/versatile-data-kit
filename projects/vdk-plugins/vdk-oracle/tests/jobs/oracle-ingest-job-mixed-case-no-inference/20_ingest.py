# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime


def run(job_input):
    payloads = [
        # Schema wil be inferred but nothing will be ingested
        {
            "Id": 1,
            "Str_Data": "string",
            "Int_Data": 12,
            "Float_Data": 1.2,
            "Bool_Data": True,
            "Timestamp_Data": datetime.datetime.utcfromtimestamp(1700554373),
        },
        {
            "Id": 2,
            "Str_Data": "string",
            "Int_Data": 12,
            "Float_Data": 1.2,
            "Bool_Data": True,
            "Timestamp_Data": datetime.datetime.utcfromtimestamp(1700554373),
        },
    ]
    for payload in payloads:
        job_input.send_object_for_ingestion(
            payload=payload, destination_table="oracle_ingest_mixed_case_no_inference"
        )
