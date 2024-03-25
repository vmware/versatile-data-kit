# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0


def run(job_input):
    frost = """The woods are lovely, dark and deep,
But I have promises to keep,
And miles to go before I sleep,
And miles to go before I sleep.
"""
    payload_with_blob = {
        "ID": 5,
        "BLOB_DATA": frost.encode("utf-8"),
    }

    job_input.send_object_for_ingestion(
        payload=payload_with_blob, destination_table="TEST_TABLE"
    )
