# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
import logging

import pandas as pd
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Download datasets required by the scenario and put them in the data lake.
    """
    log.info(f"Starting job step {__name__}")

    url = "https://www.bea.gov/sites/default/files/2021-12/lagdp1221.xlsx"

    df = pd.read_excel(url, header=3, na_values="(NA)").replace("'", "''", regex=True)

    # select only interesting rows
    df = df[["Unnamed: 0", 2017, 2018, 2019, 2020]]
    df.rename(
        {
            "Unnamed: 0": "County",
            2017: "Year2017",
            2018: "Year2018",
            2019: "Year2019",
            2020: "Year2020",
        },
        axis=1,
        inplace=True,
    )
    df.dropna(axis=0, inplace=True)

    job_input.send_tabular_data_for_ingestion(
        df.itertuples(index=False),
        destination_table="us_gdp",
        column_names=df.columns.tolist(),
    )
