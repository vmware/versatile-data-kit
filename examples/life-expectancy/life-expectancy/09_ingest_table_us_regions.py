# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
import logging

import pandas as pd
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Download datasets required by the scenario and put them in the data data lake.
    """
    log.info(f"Starting job step {__name__}")

    # url of the U.S. Life Expectancy at Birth by State and Census Tract - 2010-2015 dataset
    url = "https://raw.githubusercontent.com/cphalpert/census-regions/master/us%20census%20bureau%20regions%20and%20divisions.csv"

    df = pd.read_csv(url, sep=",")

    df.columns = df.columns.str.replace(" ", "")

    job_input.send_tabular_data_for_ingestion(
        df.itertuples(index=False),
        destination_table="us_regions",
        column_names=df.columns.tolist(),
    )
