# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pandas as pd
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    # The job only uses job_input.get_managed_connection to check it is initialized properly
    # Should not use job_input.execute_query

    data = {"product_name": ["Computer", "Tablet"], "price": [900, 300]}
    df = pd.DataFrame(data, columns=["product_name", "price"])
    df.to_sql(
        "test_table",
        job_input.get_managed_connection(),
        if_exists="replace",
        index=False,
    )

    df = pd.read_sql("select * from test_table", con=job_input.get_managed_connection())
    assert len(df) > 0
