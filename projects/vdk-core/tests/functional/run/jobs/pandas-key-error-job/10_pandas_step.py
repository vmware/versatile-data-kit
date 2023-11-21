# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pandas as pd
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    df1 = pd.DataFrame({"lkey": ["foo", "bar", "baz", "foo"], "value": [1, 2, 3, 5]})
    df2 = pd.DataFrame({"rkey": ["foo", "bar", "baz", "foo"], "value": [5, 6, 7, 8]})
    pd.merge(
        df1,
        df2,
        how="inner",
        on=[
            "timestamp",
            "status_code",
            "response_status",
            "exception",
            "region",
            "region_type",
            "tenant",
            "utc_time",
        ],
    )
