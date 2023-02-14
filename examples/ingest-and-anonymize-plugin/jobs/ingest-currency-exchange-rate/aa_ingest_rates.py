# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import requests
import xmltodict
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Function named `run` is required in order for a python script to be recognized as a Data Job Python step and executed.

    VDK provides to every python step an object - job_input - that has methods for:

    * executing queries to OLAP Database;
    * ingesting data into a database;
    * processing data into a database.
    See IJobInput documentation for more details.
    """

    # we are using http just as an example. But in reality the source could be anything - S3, file share, database, etc.)
    response = requests.get(
        "https://api.nbp.pl/api/exchangerates/rates/c/eur/2011-01-01/2012-01-01/?format=xml"
    )

    def ingest(_, data):
        job_input.send_object_for_ingestion(
            payload=data, destination_table="exchange_rates_series"
        )
        return True

    xmltodict.parse(response.content, item_depth=3, item_callback=ingest)
