# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Iterable
from typing import List
from typing import Optional

from vdk.plugin.data_sources.config import config_class
from vdk.plugin.data_sources.config import config_field
from vdk.plugin.data_sources.data_source import DataSourcePayload
from vdk.plugin.data_sources.data_source import IDataSource
from vdk.plugin.data_sources.data_source import (
    IDataSourceConfiguration,
)
from vdk.plugin.data_sources.data_source import IDataSourceStream
from vdk.plugin.data_sources.factory import data_source
from vdk.plugin.data_sources.state import IDataSourceState
from vdk.plugin.singer import message_utils
from vdk.plugin.singer.adapter import Catalog
from vdk.plugin.singer.adapter import CatalogEntry
from vdk.plugin.singer.adapter import Schema
from vdk.plugin.singer.tap_command import TapCommandRunner

log = logging.getLogger(__name__)

DESCRIPTION = """Singer Taps as data sources within the Versatile Data Kit.
To see list of Singer taps use vdk singer --list-taps.
For more check documentation at https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-singer
"""


@config_class("singer-tap", DESCRIPTION)
class SingerDataSourceConfiguration(IDataSourceConfiguration):
    tap_name: str = config_field(
        description="The tap name of the singer data source for example tap-salesforce or tap-postgres"
    )
    tap_config: dict = config_field(
        description="Configuration values as per the official documentation of the singer tap."
    )
    tap_auto_discover_schema: bool = config_field(
        description="On run it will automatically discover the schema if the tap supports",
        default=True,
    )


class SingerDataSourceStream(IDataSourceStream):
    def __init__(
        self,
        tap_name: str,
        stream_name: str,
        config: dict,
        catalog: Optional[dict] = None,
        state: Optional[dict] = None,
    ):
        self._tap_name = tap_name
        self._stream_name = stream_name
        self._config = config
        self._catalog = catalog
        self._state = state

    def name(self) -> str:
        return self._stream_name

    def read(self) -> Iterable[DataSourcePayload]:
        log.debug(
            f"Starting to read data source {self._tap_name} stream {self._stream_name}."
        )
        with TapCommandRunner() as tap_command:
            tap_command: TapCommandRunner
            messages = tap_command.sync(
                self._tap_name,
                config=self._config,
                catalog=self._catalog,
                state=self._state,
            )
            for msg in messages:
                payload = message_utils.convert_message_to_payload(msg)
                if payload:
                    yield payload


@data_source(name="singer-tap", config_class=SingerDataSourceConfiguration)
class SingerDataSource(IDataSource):
    def __init__(self):
        self._config = None
        self._streams: List[SingerDataSourceStream] = []

    def configure(self, config: SingerDataSourceConfiguration):
        self._config = config

    def connect(self, state: IDataSourceState):
        if self._streams:
            log.warning(
                f"Ignoring second call to {SingerDataSource.__name__}.connect method"
            )
            return None

        catalog = Catalog([])
        # TODO get catalog from state
        if self._config.tap_auto_discover_schema:
            catalog = self.__discover_schema(self._config)
            # save catalog in state

        for stream in catalog.streams:
            data_stream = SingerDataSourceStream(
                tap_name=self._config.tap_name,
                stream_name=stream.tap_stream_id,
                config=self._config.tap_config,
                catalog={"streams": [stream.to_dict()]},
            )
            self._streams.append(data_stream)

    @staticmethod
    def __discover_schema(config: SingerDataSourceConfiguration) -> Catalog:
        with TapCommandRunner() as runner:
            catalog = runner.discover(config.tap_name, config=config.tap_config)

        if not catalog.streams:
            log.info(
                f"No streams discovered  in the tap {config.tap_name}."
                f" Will create single data stream for all the data"
            )
            entry = CatalogEntry()
            entry.tap_stream_id = config.tap_name
            entry.stream = config.tap_name
            entry.key_properties = {}
            entry.schema = Schema()  # TODO: auto infer it from the data
            catalog = Catalog([entry])

        return catalog

    def disconnect(self):
        # TODO? or not needed?
        pass

    def streams(self) -> List[IDataSourceStream]:
        return self._streams.copy()
