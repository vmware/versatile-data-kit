# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import math
from typing import Any
from typing import List
from typing import Optional
from typing import Type

from trino.dbapi import Cursor
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import UserCodeError

log = logging.getLogger(__name__)


class IngestToTrino(IIngesterPlugin):
    """
    Create a new ingestion mechanism for ingesting to a Trino database
    """

    def __init__(self, context: JobContext):
        self.context = context

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str] = None,
        target: str = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ) -> None:
        """
        Performs the ingestion
        :param payload:
            the payload to be ingested
        :param destination_table:
            the name of the table receiving the payload in the target database
        :param target:
            this parameter is currently unused
            TODO: figure out what to use target for
        :param collection_id:
            an identifier specifying that data from different method
            invocations belongs to the same collection
        :param metadata:
            an IngestionMetadata object that contains metadata about the
            pre-ingestion and ingestion operations
        """

        log.info(
            f"Ingesting payloads to table: {destination_table} in Trino database; "
            f"collection_id: {collection_id}"
        )

        with self.context.connections.open_connection("TRINO").connect() as conn:
            cur = conn.cursor()
            self._ingest_payload(destination_table, cur, payload)

    def _ingest_payload(
        self, destination_table: str, cur: Cursor, payload: List[dict]
    ) -> None:
        # the max http header needs to increase for a payload of 1 million rows, here it's 10 times the default
        import http

        http.client._MAXLINE = 6553600

        query, fields, types = self._create_query_and_fields(
            destination_table, len(payload), cur
        )

        try:
            payload = self.__lowercase_keys_in_payload(payload)
            params = self.__get_values_for_fields(payload, fields, types)
            cur.execute(query, params)
            cur.fetchall()
            log.debug("Payload was ingested.")
        except Exception as e:
            errors.log_and_rethrow(
                errors.find_whom_to_blame_from_exception(e),
                log,
                f"Failed to sent payload into table {destination_table}",
                "Unknown error. Error message was : " + str(e),
                "Will not be able to send the payload for ingestion",
                "See error message for help ",
                e,
                wrap_in_vdk_error=True,
            )

    @staticmethod
    def __to_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value == "true" or value == "True":
            return True
        if value == "false" or value == "False":
            return False
        raise ValueError("bool cast accept only True/true/False/false values.")

    def __cast(self, key: str, new_value: Any, value_type: Type) -> Any:
        try:
            log.debug(f"Cast {key} to type {value_type}")
            if value_type == bool:
                return self.__to_bool(new_value)
            if value_type == float:
                value_with_float_type = float(new_value)
                if math.isnan(value_with_float_type):
                    return None
                else:
                    return value_with_float_type
            else:
                return value_type(new_value)
        except Exception as e:
            raise UserCodeError(
                ErrorMessage(
                    "Cannot ingest payload.",
                    f"The value of the passed with field key (or column name) {key} is not expected type. "
                    f"Expected field type is {value_type}. ",
                    f"We could not convert the value to that type. Error is {e}",
                    f"In order to ensure that we do not overwrite with bad value, "
                    f"the operation aborts.",
                    "Inspect the job code and fix the passed data column names or dictionary keys",
                )
            ) from e

    @staticmethod
    def __trino_type_to_python_type_map(trino_type: str):
        trino_type = trino_type.lower()
        if "varchar" in trino_type:
            return str
        if trino_type in ("double", "real"):
            return float
        if "decimal" in trino_type:
            return float
        if "boolean" == trino_type:
            return bool
        if trino_type in ("bigint", "tinyint", "integer", "smallint"):
            return int
        # default to string
        return str

    def __get_values_for_fields(self, payload: List[dict], fields: list, types: list):
        types_dict = dict()
        for field, field_type in zip(fields, types):
            types_dict[field] = self.__trino_type_to_python_type_map(field_type)

        params = []
        for obj in payload:
            for field in fields:
                if field.lower() in obj:
                    params.append(
                        self.__cast(
                            field.lower(), obj[field.lower()], types_dict[field.lower()]
                        )
                    )
                else:
                    params.append(None)

        return params

    @staticmethod
    def __lowercase_keys_in_payload(payload):
        new_payload = []
        for obj in payload:
            new_obj = dict()
            for k, v in obj.items():
                new_obj[k.lower()] = v
            new_payload.append(new_obj)
        return new_payload

    def _create_query_and_fields(
        self, destination_table: str, payload_size: int, cur: Cursor
    ) -> (str, List[str]):
        """
        Returns a tuple of the insert query and the list of fields in the destination table;
        for a table dest_table with fields val1, val2 and batch_size 3, this method will return:
        'INSERT INTO dest_table (val1, val2) VALUES (?, ?), (?, ?), (?, ?)', ['val1', 'val2']

        :param destination_table: the name of the destination table
        :param cur: the database cursor
        :param batch_size: the size of the batch of rows to be ingested
        :return: a tuple containing the query and list of fields
        """

        cur.execute(f"SHOW COLUMNS FROM {destination_table}")
        columns_info = cur.fetchall()
        fields = [field_tuple[0] for field_tuple in columns_info]
        types = [field_tuple[1] for field_tuple in columns_info]

        row_to_be_replaced = f"({', '.join('?' for field in fields)})"

        return (
            f"INSERT INTO {destination_table} ({', '.join(fields)}) VALUES {', '.join([row_to_be_replaced for i in range(payload_size)])}",
            fields,
            types,
        )
