# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from collections import OrderedDict

import pyarrow
from vdk.internal.core import errors
from vdk.plugin.impala import impala_error_classifier
from vdk.plugin.impala.impala_connection import ImpalaConnection


class ImpalaHelper:
    def __init__(self, db_connection: ImpalaConnection) -> None:
        self._log = logging.getLogger(__name__)
        self._db_connection = db_connection

    def get_table_description(self, table_name):
        self._log.debug(f"Retrieving details for table {table_name}.")
        try:
            return self._db_connection.execute_query(f"DESCRIBE formatted {table_name}")
        except Exception as e:
            if impala_error_classifier._is_authorization_error(e):
                errors.log_and_throw(
                    to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                    log=self._log,
                    what_happened=f"Data loading into table {table_name} has failed.",
                    why_it_happened=(
                        f"You are trying to load data into a table which you do not have access to or it does not "
                        f"exist: {table_name}."
                    ),
                    consequences="Data load will be aborted.",
                    countermeasures="Make sure that the destination table exists and you have access to it.",
                )
            else:
                raise e

    def __get_table_schema(self, table_description, section_start="#", second_end="#"):
        """
        Gets column names and data types from Impala table.
        It would be a lot more easier to execute pure describe statement, but then we will execute 2 describe statements
        to get the table schema and check if the table is stored as parquet
        Will return the full table schema including partition columns order the same way as in Impala
        """
        self._log.debug("Retrieving destination table schema.")
        column_name_to_column_type_map = OrderedDict()
        is_in_columns_section = False
        searched_section_ended = False
        searched_sectioned_started = False
        for (
            column_name,
            column_type,
            _,
        ) in table_description:  # 3rd value is column comment
            if column_name is None or column_name.strip() == "":
                continue
            if column_name.startswith(section_start):  # new section begins
                searched_sectioned_started = True
            if searched_sectioned_started and not is_in_columns_section:
                if column_name.strip() == "# col_name":  # column info follows
                    is_in_columns_section = True
                else:
                    is_in_columns_section = False
                continue
            if searched_sectioned_started:
                if column_name.startswith(second_end):
                    searched_section_ended = True
            if is_in_columns_section and not searched_section_ended:
                column_name_to_column_type_map[
                    column_name.strip()
                ] = column_type.strip()
        return column_name_to_column_type_map

    def get_table_columns(self, table_description):
        """
        :param table_description: result of #get_table_description
        :return: dict with column name and type
        """
        return self.__get_table_schema(table_description, section_start="#")

    def get_table_partitions(self, table_description):
        """
        :param table_description: result of #get_table_description
        :return: dict with partition name and type
        """
        return self.__get_table_schema(
            table_description, section_start="# Partition Information"
        )

    def ensure_table_format_is_parquet(self, table_name, table_description):
        for key, value, _ in table_description:  # 3rd value is column comment
            # Input format of parquet table is "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
            if key is not None and key.strip() == "InputFormat:":
                if "parquet" in value:  # table is stored as parquet
                    return
                else:  # table is not stored as parquet
                    errors.log_and_throw(
                        to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                        log=self._log,
                        what_happened="Data loading has failed.",  # FIXME: this is too specific
                        why_it_happened=(
                            f"You are trying to load data into a table {table_name} with an unsupported format. "
                            f"Currently only Parquet table format is supported."
                        ),
                        consequences="Data load will be aborted.",  # FIXME: this is too specific
                        countermeasures=(
                            "Make sure that the destination table is stored as parquet: "
                            "https://www.cloudera.com/documentation/enterprise/5-11-x/topics/impala_parquet.html"
                            "#parquet_ddl"
                        ),
                    )
        # TODO once there is more robust loading implemented the below error can be removed. We can try to load even if
        # we cannot determine the table storage type
        errors.log_and_throw(
            to_be_fixed_by=errors.ResolvableBy.PLATFORM_ERROR,
            log=self._log,
            what_happened="Cannot determine the target table file format, which is needed to load data into it.",
            why_it_happened="There's a bug in VDK code.",
            consequences="Application will exit.",
            countermeasures="Report this bug to versatile data kit team.",
        )

    def generate_parquet_schema_from_table_schema(self, table_columns):
        """
        Builds the parquet schema based on the column types and order in the target table, in order to ensure the new file
        will be compatible with the table
        """
        self._log.debug("Generating parquet file schema from table schema.")
        impala_type_to_pyarrow_type_map = {
            "string": pyarrow.string(),
            "boolean": pyarrow.bool_(),
            "double": pyarrow.float64(),
            "float": pyarrow.float32(),
            "int": pyarrow.int32(),
            "bigint": pyarrow.int64(),
            "timestamp": pyarrow.timestamp("ns"),
        }
        # including the decimal types in the map
        for precision_value in range(1, 39):
            for scale_value in range(0, precision_value + 1):
                impala_type_to_pyarrow_type_map[
                    f"decimal({precision_value},{scale_value})"
                ] = pyarrow.decimal128(precision_value, scale_value)

        parquet_schema = []
        for column_name, column_type in table_columns.items():
            parquet_schema.append(
                (column_name, impala_type_to_pyarrow_type_map[column_type])
            )
        return pyarrow.schema(parquet_schema)

    def get_parquet_schema(self, table):
        table_description = self.get_table_description(table)
        self.ensure_table_format_is_parquet(table, table_description)
        table_columns = self.get_table_columns(table_description)
        return self.generate_parquet_schema_from_table_schema(table_columns)

    @staticmethod
    def get_insert_sql_partition_clause(partitions):
        # https://docs.cloudera.com/documentation/enterprise/6/6.3/topics/impala_insert.html

        # NOTE: https://github.com/kayak/pypika looks interesting if we start having more complex query buildings
        sql = "PARTITION (" + ",".join("`" + p + "`" for p in partitions.keys()) + ")"
        return sql
