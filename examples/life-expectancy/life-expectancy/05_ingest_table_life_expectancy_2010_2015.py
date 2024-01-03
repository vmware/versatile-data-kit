# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
import logging

import numpy as np
import pandas as pd
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Download datasets required by the scenario and put them in the data lake.
    """
    log.info(f"Starting job step {__name__}")

    # url of the U.S. Life Expectancy at Birth by State and Census Tract - 2010-2015 dataset
    url = "http://data.cdc.gov/api/views/5h56-n989/rows.csv"

    dtypes = {
        "State": str,
        "County": str,
        "Census Tract Number": str,
        "Life Expectancy": np.float64,
        "Life Expectancy Range": str,
        "Life Expectancy Standard Error": np.float64,
    }

    df = pd.read_csv(url, dtype=dtypes).replace("'", "''", regex=True)

    df.columns = df.columns.str.replace(" ", "")

    job_input.send_tabular_data_for_ingestion(
        df.itertuples(index=False),
        destination_table="life_expectancy_2010_2015",
        column_names=df.columns.tolist(),
    )
