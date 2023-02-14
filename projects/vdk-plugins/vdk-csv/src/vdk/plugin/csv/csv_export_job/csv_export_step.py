# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import csv
import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


class CsvExporter:
    def __init__(self, job_input: IJobInput):
        self.__job_input = job_input

    def export(self, query: str, fullpath: str):
        query_result = self.__job_input.execute_query(query)
        with open(fullpath, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            for row in query_result:
                writer.writerow(row)
        log.info(f"Exported data successfully.You can find the result here: {fullpath}")


def run(job_input: IJobInput) -> None:
    query = job_input.get_arguments().get("query")
    fullpath = job_input.get_arguments().get("fullpath")
    exporter = CsvExporter(job_input)
    exporter.export(query, fullpath)
