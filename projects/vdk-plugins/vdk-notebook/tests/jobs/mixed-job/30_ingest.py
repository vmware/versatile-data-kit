# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0


def run(job_input):
    payload = {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False}

    job_input.send_object_for_ingestion(
        payload=payload, destination_table="rest_target_table"
    )
