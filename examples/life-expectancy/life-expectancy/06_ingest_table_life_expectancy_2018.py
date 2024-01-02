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
    Download datasets required by the scenario and store in the data lake.
    """
    log.info(f"Starting job step {__name__}")

    # url of the U.S. Life Expectancy at Birth by State and Census Tract - 2018 dataset
    url = "http://data.cdc.gov/api/views/a5a8-jsrq/rows.csv"

    dtypes = {
        "State": str,
        "Sex": str,
        "LEB": np.float64,
        "SE": np.float64,
        "Quartile": str,
    }

    df = pd.read_csv(url, dtype=dtypes, na_values="*")

    job_input.send_tabular_data_for_ingestion(
        df.itertuples(index=False),
        destination_table="life_expectancy_2018",
        column_names=df.columns.tolist(),
    )
