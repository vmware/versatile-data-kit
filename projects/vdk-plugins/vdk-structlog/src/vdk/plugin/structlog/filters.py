# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from logging import Filter
from logging import LogRecord
from typing import Set

from vdk.plugin.structlog.constants import RECORD_DEFAULT_FIELDS
from vdk.plugin.structlog.constants import STRUCTLOG_METADATA_FIELDS


class JsonMetadataFilter(Filter):
    """
    Modifies log records when json formatting is used.
    Removes the metadata fields that are not part of the metadata config.
    The json formatter displays all custom fields by default, so if they're not
    part of the metadata config, they should be removed in order for filtering
    to work.
    """

    def __init__(self, key_set: Set):
        super().__init__()
        self._key_set = {
            STRUCTLOG_METADATA_FIELDS[k] if k in STRUCTLOG_METADATA_FIELDS else k
            for k in key_set
        }

    def filter(self, record: LogRecord) -> LogRecord:
        fields = vars(record)
        for field in fields:
            if field not in self._key_set and field not in RECORD_DEFAULT_FIELDS:
                # not sure if we want to delete, e.g. delattr(record, field) or just set to empty
                setattr(record, field, "")
        return record


class ConsoleMetadataFilter(Filter):
    """
    Modifies log records when console formatting is used
    Sets metadata fields that are in the config set but not in the log record to empty string.
    This prevents the formatter from breaking for different records, e.g. some records have vdk_job_name and some don't
    and records that don't have vdk_job_name should still have vdk_job_name in order not to break the formatter.
    """

    def __init__(self, key_set: Set):
        super().__init__()
        self._key_set = key_set

    def filter(self, record: LogRecord) -> LogRecord:
        fields = vars(record)
        for field in self._key_set:
            if field not in fields and field not in RECORD_DEFAULT_FIELDS:
                setattr(record, field, "")
        return record


class AttributeAdder(Filter):
    """
    Adds attributes to log records.
    """

    def __init__(self, attr_key: str, attr_value: str):
        super().__init__()
        self._attr_key = attr_key
        self._attr_value = attr_value

    def filter(self, record: LogRecord) -> LogRecord:
        setattr(record, self._attr_key, self._attr_value)
        return record
