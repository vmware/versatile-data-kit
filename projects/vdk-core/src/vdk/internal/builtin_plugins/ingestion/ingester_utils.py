# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Ingestion Utilities
"""
import datetime
import itertools
import logging
import queue
import threading
import uuid
from decimal import Decimal
from json import JSONEncoder
from typing import Any
from typing import List
from typing import Optional

from vdk.internal.builtin_plugins.ingestion.exception import (
    InvalidArgumentsIngestionException,
)
from vdk.internal.builtin_plugins.ingestion.exception import PayloadIngestionException
from vdk.internal.core import errors
from vdk.internal.core.errors import ResolvableBy

log = logging.getLogger(__name__)


class AtomicCounter:
    """
    Thread-safe incrementing counter
    """

    def __init__(self, start: int = 0):
        """Init a new atomic counter to start value"""
        self.value: int = start
        self._lock = threading.Lock()

    def increment(self, step: int = 1) -> int:
        """Atomically increment the counter by step, return new value"""
        self.get_and_increment(step)
        return self.value

    def get_and_increment(self, step: int = 1) -> int:
        """Atomically increment counter by step, return old value"""
        with self._lock:
            old_value: int = self.value
            self.value += step
            return old_value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self)


class IngesterJsonEncoder(JSONEncoder):
    """
    This class is used to avoid an issue with the __verify_payload_format serialization check.
    Normally, including data of type Decimal and datetime would cause that check to fail so we've amended
    the default JsonEncoder object used to convert Decimal and datetime values to floats to avoid this issue.
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.timestamp()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return list(obj)
        return super().default(obj)


def get_page_generator(rows, page_size=10000):
    # TODO add support for Pandas
    if hasattr(rows, "fetchmany"):
        while True:
            page = rows.fetchmany(page_size)
            if not page:
                return
            yield page
    elif hasattr(rows, "__iter__") or hasattr(rows, "__getitem__"):
        it = iter(rows)
        while True:
            page = list(itertools.islice(it, page_size))
            if not page:
                return
            yield page
    else:
        raise InvalidArgumentsIngestionException(
            param_name="rows",
            param_constraint="rows is a python iterator or database cursor",
            actual_value=type(rows),
            resolvable_by=ResolvableBy.USER_ERROR,
        )


def validate_column_count(
    data: iter, column_names: iter, destination_table: str, target: str
):
    if data:
        if len(column_names) != len(data[0]):
            errors.report_and_throw(
                PayloadIngestionException(
                    message=f"Failed to post tabular data for ingestion "
                    f"for table {destination_table} and target {target}."
                    "The number of column names are not matching the number of values in at least on of"
                    f"the rows. You provided columns: '{column_names}' and data row: "
                    f"'{data[0]}'"
                    + "Check the data and the column names you are providing, their count should match.",
                    payload_id=get_payload_id_for_debugging(data[0]),
                    destination_table=destination_table,
                    target=target,
                )
            )


def convert_table(table: iter, column_names: iter) -> List[dict]:
    """
    Converts tabular data into dictionary objects

    :param table: iter
       A representation of a two-dimensional array that allows iteration over rows.
    :param column_names: iter
       Names of the table columns.
    :return: list of dicts containing the converted table objects.
    """
    converted_rows = []
    for row in table:
        cdf_row = dict()
        for index, value in enumerate(row):
            value = _handle_special_types(value)
            cdf_row[column_names[index]] = value
        converted_rows.append(cdf_row)

    return converted_rows


def _handle_special_types(value: Any) -> Any:
    """
    Handle data types that require special care to be correctly processed.

    :param value: Any
        The value to be converted. Only `datetime.date` and `uuid.UUID` objects
        are converted. All other data types are returned as is.
    """
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(
            value
        )  # there is no default json serializer for UUID type, hence cast to string
    return value


def wait_completion(objects_queue: queue.Queue, payloads_queue: queue.Queue):
    objects_queue.join()
    payloads_queue.join()


def is_iterable(obj: Any) -> bool:
    """
    According to Python doc this is the most reliable way to determine if object is iterable.
    See https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable
    :param obj: the object to check
    :return: true or false :)
    """
    try:
        _ = iter(obj)
        return True
    except TypeError:
        return False


def get_payload_id_for_debugging(payload_dict: dict) -> Optional[str]:
    if isinstance(payload_dict, dict):
        payload_id = payload_dict.get("@id", payload_dict.get("id", ""))[0:20]
        return str(payload_id)
    return None
