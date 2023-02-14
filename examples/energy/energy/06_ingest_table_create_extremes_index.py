# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
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

    # url of the U.S. Climate Extremes Index (CEI) dataset
    url = "https://www.ncdc.noaa.gov/extremes/cei/graph/us/01-12/2/data.csv"

    dtypes = {
        "Date": str,
        "MuchAboveNormal": np.float64,
        "MuchBelowNormal": np.float64,
    }

    df = pd.read_csv(url, skiprows=[0], dtype=dtypes)

    df.columns = df.columns.str.replace(" ", "")

    job_input.send_tabular_data_for_ingestion(
        df.itertuples(index=False),
        destination_table="climate_extremes_index",
        column_names=df.columns.tolist(),
    )
