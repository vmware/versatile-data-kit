# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import time

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    # If db property includes catalog name, get only the schema name ('default' from 'memory.default').
    # This is done because the templates' implementation escapes db, table and column names passed as arguments, so that
    # reserved words could be used for their values
    db_name = job_input.get_property("db").split(".")[-1]

    props = job_input.get_all_properties()
    destination_table = props["ingest_destination_table"]
    id1 = props["id1"]
    id2 = props["id2"]
    id3 = props["id3"]

    timeout = int(props["ingest_timeout"])  # [seconds]
    timeout_start = time.time()

    while time.time() < timeout_start + timeout:
        # check if data was correctly ingested
        result = job_input.execute_query(
            f"SELECT id1, id2, id3 FROM {db_name}.{destination_table} "
            f"WHERE id1 = '{id1}' "
            f"AND id2 = '{id2}' "
            f"AND id3 = '{id3}'"
        )
        log.info(f"Query result: {result}")

        if result:
            if result[0][0] != id1 and result[0][1] != id2 and result[0][2] != id3:
                raise Exception("The data is not ingested correctly")
            else:
                props["succeeded"] = "true"
                break
        else:
            time.sleep(10)

    job_input.set_all_properties(props)
