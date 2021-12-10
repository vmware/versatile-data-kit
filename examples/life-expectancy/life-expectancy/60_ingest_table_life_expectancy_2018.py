import inspect
import logging
import os
import numpy as np
import pandas as pd
import sys

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
    url = 'http://data.cdc.gov/api/views/a5a8-jsrq/rows.csv'

    dtypes = {
        'State' : str,
        'Sex' : str,
        'LEB' : np.float64,
        'SE' : np.float64,
        'Quartile' : str,
    }

    df = pd.read_csv(url, dtype=dtypes, na_values='*')

    log.info(df.head(5))

     
    for i,row in df.iterrows():
        query = build_insert_query(row, df.columns.tolist(), 'life_expectancy_2018')
        
        job_input.execute_query(query)
