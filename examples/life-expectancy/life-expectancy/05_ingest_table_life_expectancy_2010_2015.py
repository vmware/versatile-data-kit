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
    Download datasets required by the scenario and put them in the data directory.
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

    #records = [row for index, row in df.iterrows()]
    job_input.send_tabular_data_for_ingestion(df.itertuples(index=False), destination_table="life_expectancy_2010_2015", column_names=df.columns, method='trino')
    #for i, row in df.iterrows():
    #    query = build_insert_query(
    #        row, df.columns.tolist(), "life_expectancy_2010_2015"
    #    )

    #    job_input.execute_query(query)
