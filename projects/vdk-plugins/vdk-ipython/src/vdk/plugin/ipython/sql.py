# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import warnings

from IPython import get_ipython
from vdk.api.job_input import IJobInput
from vdk.plugin.ipython import job
from vdk.plugin.ipython.common import show_ipython_error
from vdk.plugin.ipython.job import JobControl

log = logging.getLogger(__name__)


def vdksql(line, cell):
    """
    Execute SQL query in the given cell and return the result as a Pandas DataFrame.

    This function also auto-initializes VDK Job if it is not already
    initialized and uses its managed connection to run the query.


    :param line: str
            Not used in this function but required for cell magic.
    :param cell: str
            The SQL query to be executed.

    :returns: pd.DataFrame or None
            Result of the SQL query as a Pandas DataFrame or None for DDL/DML statements.
            The dataframe is not available in the cells, but it provides nice visualization

    Raises:
        Exception if any error occurs during query execution or VDK initialization.
    """

    vdk: JobControl = get_ipython().user_global_ns.get("VDK", None)
    if not vdk:
        log.warning(
            "VDK is not initialized with '%reload_VDK'. "
            "Will auto-initialize now wth default parameters."
        )
        job.load_job()
        vdk = get_ipython().user_global_ns.get("VDK", None)
        if not vdk:
            message = "VDK cannot initialized. Please execute: %reload_VDK"
            show_ipython_error(message)
            return None

    job_input: IJobInput = vdk.get_initialized_job_input()

    try:
        # purposely in local scope as pandas is not required dependency for the plugin
        import pandas as pd

        conn = job_input.get_managed_connection()
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                result_df = pd.read_sql(cell, conn)
            if result_df is None:
                return "No result."
            return prepare_result_cell_output(result_df)
        except Exception as e:
            if "object is not iterable" in str(e):
                # DDL or DML statement we ignore output
                return "Query statement executed successfully."
            else:
                show_ipython_error(str(e))
    except Exception as e:
        show_ipython_error(str(e))


def prepare_result_cell_output(result_df):
    # the configuration is provided for use in tests
    if os.environ.get("USE_DEFAULT_CELL_TABLE_OUTPUT", "no") in ["true", "t", "1", "y"]:
        return result_df

    try:
        return prepare_result_cell_output_ipyaggrid(result_df)
    except ImportError:
        log.info(
            "ipyaggrid is not installed. "
            "If installed result would be formatted in an interactive grid."
        )
        return result_df
    except Exception as e:
        log.error(
            "There was an issue rendering the query result output using ipyaggrid. "
            f"Error was {str(e)} "
            "Consider reinstalling the package if needed."
            "Falling back to default table visualization"
        )
        return result_df


def prepare_result_cell_output_ipyaggrid(result_df):
    import ipyaggrid

    custom_columns = [
        {
            "field": col,
            "headerName": f"{col} ({result_df[col].dtype})",
            "sortable": True,
            "resizable": True,
        }
        for col in result_df.columns
    ]
    grid_options = {
        "columnDefs": custom_columns,
        "pagination": True,
        "paginationPageSize": 50,
        "sideBar": ["columns", "filters", "export"],
    }
    grid = ipyaggrid.Grid(grid_data=result_df, grid_options=grid_options)
    return grid
