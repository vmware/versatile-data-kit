# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import requests


def run(job_input):
    response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    response.raise_for_status()
    payload = response.json()

    job_input.send_object_for_ingestion(
        payload=payload, destination_table="rest_target_table"
    )
