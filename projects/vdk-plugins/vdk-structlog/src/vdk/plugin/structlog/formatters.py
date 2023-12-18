# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from logging import Filter
from logging import Formatter
from logging import LogRecord
from typing import Any
from typing import Dict

from pythonjsonlogger import jsonlogger
from vdk.plugin.structlog.constants import CONSOLE_STRUCTLOG_LOGGING_METADATA_ALL
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_METADATA_ALL
from vdk.plugin.structlog.filters import ConsoleMetadataFilter
from vdk.plugin.structlog.filters import JsonMetadataFilter


class JsonFormatter(jsonlogger.JsonFormatter):
    """
    Json formatter. Shows all log record fields by default.
    Removes log record fields that are empty. Adds timestamp
    and level fields to the log output.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        # remove log record fields that are set to empty string
        keys = [x for x in record.__dict__.keys() if record.__dict__[x] == ""]
        for key in keys:
            del record.__dict__[key]
        super().add_fields(log_record, record, message_dict)
        if log_record.get("levelname"):
            log_record["level"] = record.levelname.upper()
            del log_record["levelname"]
        if log_record.get("created"):
            log_record["timestamp"] = record.created
            del log_record["created"]


class LtsvFormatter(Formatter):
    """
    Formats logs in the Labelled Tab Separated Values (LTSV) format.
    You can read more about this format here: http://ltsv.org/

    """

    def format(self, record: LogRecord) -> LogRecord:
        record.message = record.getMessage()
        record.timestamp = self.formatTime(record, self.datefmt)
        record.line_number = record.lineno
        if ("level" not in record.__dict__) or (not record.__dict__["level"]):
            record.level = record.levelname

        s = self.formatMessage(record)
        return s


class ConsoleFormatter(Formatter):
    """
    Console formatter. Basically the same as logging.Formatter.
    Log records should be modified in filters. Message and exception
    formatting should be modified here.
    """

    def format(self, record: LogRecord) -> LogRecord:
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s


class StructlogMetadataBuilder:
    """
    Builds output format strings in % style for
    different formats.

    For json, it appends %({key}s) formatting strings

    For console, it takes into account the actual
    record field names and appends those to the output
    format string
    """

    def __init__(self, metadata_keys: str):
        self._metadata_keys = metadata_keys.split(",")

    def build_json_format(self) -> str:
        out = []
        for key in self._metadata_keys:
            if key in STRUCTLOG_LOGGING_METADATA_ALL:
                out.append(STRUCTLOG_LOGGING_METADATA_ALL[key])
            else:
                out.append(f"%({key})s")
        out.append("%(message)s")
        return " ".join(out)

    def build_console_format(self) -> str:
        out = []
        for key in self._metadata_keys:
            if key in CONSOLE_STRUCTLOG_LOGGING_METADATA_ALL:
                out.append(CONSOLE_STRUCTLOG_LOGGING_METADATA_ALL[key])
            else:
                out.append(f"%({key})s")
        out.append("- %(message)s")
        return " ".join(out)

    def build_ltsv_format(self) -> str:
        out = []
        for key in self._metadata_keys:
            if key in STRUCTLOG_LOGGING_METADATA_ALL:
                out.append(key + ":" + STRUCTLOG_LOGGING_METADATA_ALL[key])
            else:
                out.append(key + ":" + f"%({key})s")
        out.append("message:%(message)s")
        ltsv_format = "\t".join(out)
        return ltsv_format


def create_formatter(
    logging_format: str, metadata_keys: str, custom_console_format: str = None
) -> [Formatter, Filter]:
    """
    Creates a formatter and a filter based on the logging format configuration
    and metadata_keys configuration that are passed. The formatter takes care
    of the output format and the filter makes sure that only the provided
    metadata keys' values are displayed in log output.
    """
    key_set = set(metadata_keys.split(","))
    formatter = None
    custom_key_filter = None
    if logging_format == "json":
        formatter = JsonFormatter(
            StructlogMetadataBuilder(metadata_keys).build_json_format()
        )
        custom_key_filter = JsonMetadataFilter(key_set)
    elif logging_format == "ltsv":
        formatter = LtsvFormatter(
            fmt=StructlogMetadataBuilder(metadata_keys).build_ltsv_format()
        )
        custom_key_filter = ConsoleMetadataFilter(key_set)
    elif logging_format == "console":
        format_string = (
            custom_console_format
            if custom_console_format
            else StructlogMetadataBuilder(metadata_keys).build_console_format()
        )
        formatter = ConsoleFormatter(fmt=format_string)
        custom_key_filter = ConsoleMetadataFilter(key_set)
    custom_key_filter.name = "metadata_filter"
    return formatter, custom_key_filter
