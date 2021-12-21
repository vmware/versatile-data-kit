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
    Download datasets required by the scenario and put them in the data data lake.
    """
    log.info(f"Starting job step {__name__}")

    # url of the U.S. Life Expectancy at Birth by State and Census Tract - 2010-2015 dataset
    url = "https://raw.githubusercontent.com/cphalpert/census-regions/master/us%20census%20bureau%20regions%20and%20divisions.csv"

    df = pd.read_csv(url, sep=",")

    df.columns = df.columns.str.replace(" ", "")

    for i, row in df.iterrows():
        query = build_insert_query(row, df.columns.tolist(), "us_regions")

        job_input.execute_query(query)
