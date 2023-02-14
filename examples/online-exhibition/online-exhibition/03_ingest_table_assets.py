# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
import logging
import os

import pandas as pd
import requests
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Download datasets required by the scenario and put them in the data lake.
    """
    log.info(f"Starting job step {__name__}")

    api_key = job_input.get_property("api_key")

    start = 1
    rows = 100
    basic_url = f"https://api.europeana.eu/record/v2/search.json?wskey={api_key}&query=who:%22Vincent%20Van%20Gogh%22"
    url = f"{basic_url}&rows={rows}&start={start}"

    response = requests.get(url)
    response.raise_for_status()
    payload = response.json()
    n_items = int(payload["totalResults"])

    while start < n_items:
        if start > n_items - rows:
            rows = n_items - start + 1

        url = f"{basic_url}&rows={rows}&start={start}"
        response = requests.get(url)
        response.raise_for_status()
        payload = response.json()["items"]

        df = pd.DataFrame(payload)
        job_input.send_tabular_data_for_ingestion(
            df.itertuples(index=False),
            destination_table="assets",
            column_names=df.columns.tolist(),
        )
        start = start + rows

    # df = pd.read_csv(url, dtype=dtypes).replace("'", "''", regex=True)

    # df.columns = df.columns.str.replace(" ", "")

    # job_input.send_tabular_data_for_ingestion(
    #    df.itertuples(index=False),
    #    destination_table="life_expectancy_2010_2015",
    #    column_names=df.columns.tolist(),
    # )
