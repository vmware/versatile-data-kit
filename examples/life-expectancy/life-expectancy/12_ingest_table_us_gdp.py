# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
import logging
import os
import sys

import numpy as np
import pandas as pd


current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from le_utils.utils import build_insert_query

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

    for i, row in df.iterrows():
        log.info(row)
        query = build_insert_query(row, df.columns.tolist(), "us_gdp")

        job_input.execute_query(query)
