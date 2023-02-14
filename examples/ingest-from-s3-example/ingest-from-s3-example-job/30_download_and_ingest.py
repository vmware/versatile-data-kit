# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import csv

import boto3
from botocore import UNSIGNED
from botocore.client import Config


def run(job_input):
    s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    s3.download_file(
        Bucket="noaa-ghcn-pds", Key="csv/1763.csv", Filename="1763_data.csv"
    )

    with open("1763_data.csv", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)

        job_input.send_tabular_data_for_ingestion(
            rows=csv_reader,
            column_names=[
                "StationID",
                "Date",
                "Element",
                "ElementValue",
                "MFlag",
                "QFlag",
                "SFlag",
                "ObsTime",
            ],
            destination_table="noaa_ghcn_data_1763",
        )
