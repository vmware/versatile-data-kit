# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    args = job_input.get_arguments()
    props = job_input.get_all_properties()
    props["value_columns_str"] = ", ".join(
        [f'"{column}"' for column in args["value_columns"]]
    )
    props["hash_expr_str"] = ",\n".join(
        [
            f"""
                        COALESCE(CAST("{column}" AS VARCHAR), '#')
            """
            for column in args["tracked_columns"]
        ]
    ).lstrip()
    job_input.set_all_properties(props)
