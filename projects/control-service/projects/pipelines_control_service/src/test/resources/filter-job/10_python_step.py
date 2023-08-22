# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Function named `run` is required in order for a python script to be recognized as a Data Job Python step and executed.

    VDK provides to every python step an object - job_input - that has methods for:

    * executing queries to OLAP Database.
    * ingesting data into Data Lake
    * processing Data Lake data into a dimensional model Data Warehouse.

    See IJobInput documentation.
    """
    write_directory = job_input.get_temporary_write_directory()
    file_name = "example123.txt"
    file_path = write_directory.joinpath(file_name)
    with open(file_path, "a") as file:
        log.info(f"file: {file}")
        file.write("Content")

    log.info(f"file_path: {file_path}")
    log.info(f"file_name: {file_name}")
