# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import cast

from vdk.plugin.data_sources.data_source import DataSourcePayload
from vdk.plugin.singer.adapter import CatalogEntry
from vdk.plugin.singer.adapter import Message
from vdk.plugin.singer.adapter import RecordMessage
from vdk.plugin.singer.adapter import Schema
from vdk.plugin.singer.adapter import SchemaMessage
from vdk.plugin.singer.adapter import StateMessage

log = logging.getLogger(__name__)


def message_to_catalog_entry(msg: SchemaMessage):
    entry = CatalogEntry()
    entry.tap_stream_id = msg.stream
    entry.stream = msg.stream
    entry.key_properties = msg.key_properties
    entry.schema = Schema.from_dict(msg.schema)
    return entry


def convert_message_to_payload(message: Message) -> DataSourcePayload:
    if isinstance(message, RecordMessage):
        return DataSourcePayload(
            data=message.record, metadata={"time_extracted": message.time_extracted}
        )
    elif isinstance(message, StateMessage):
        return DataSourcePayload(
            data=None, metadata=None, state=cast(StateMessage, message).value
        )
    else:
        log.warning(f"Unexpected message type: {message}")
