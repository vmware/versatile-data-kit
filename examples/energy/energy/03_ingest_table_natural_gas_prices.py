# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
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

    # url of the Natural gas prices dataset
    url = "https://datahub.io/core/natural-gas/r/daily.csv"

    df = pd.read_csv(url)

    job_input.send_tabular_data_for_ingestion(
        df.itertuples(index=False),
        destination_table="natural_gas_prices",
        column_names=df.columns.tolist(),
    )
