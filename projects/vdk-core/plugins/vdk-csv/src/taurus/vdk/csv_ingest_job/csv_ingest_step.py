# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
from typing import Dict

from taurus.api.job_input import IJobInput

log = logging.getLogger(__name__)


class CsvIngester:
    def __init__(self, job_input: IJobInput):
        self.__job_input = job_input

    def ingest(self, input_file: pathlib.Path, destination_table: str, options: Dict):
        import pandas as pd

        df = pd.read_csv(str(input_file), **options)
        df.dropna(how="all", inplace=True)

        self.__job_input.send_tabular_data_for_ingestion(
            rows=df.values,
            column_names=df.columns.values.tolist(),
            destination_table=destination_table,
        )
        log.info(
            f"Ingested data from {input_file} into table {destination_table} successfully."
        )


def run(job_input: IJobInput) -> None:
    csv_file = pathlib.Path(job_input.get_arguments().get("file"))
    destination_table = job_input.get_arguments().get("destination_table", None)
    if not destination_table:
        destination_table = os.path.splitext(csv_file.name)[0]
    options = job_input.get_arguments().get("options", {})

    csv = CsvIngester(job_input)
    csv.ingest(csv_file, destination_table, options)
