# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from vdk.plugin.data_sources.data_source import DataSourcePayload


@dataclass
class SourceDefinition:
    """
    SourceDefinition class that defines the metadata and configuration for a data source.

    :param id: User provided identifier for the source "instance" which can be used to refer to that source later
    :param name: The name of the source. Must be the same name as the DataSource has been registered with (see vdk data-sources --list)
    :param config: The configuration for the source. Refer to documented data source config options (see vdk data-sources --config).
    """

    id: str
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    # TODO might be good idea to include initial state for first run
    # initial_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DestinationDefinition:
    """
    Describes the attributes and methods for a data destination.

    :param id: User provided identifier for the destination "instance" which can be used to refer to that source later.
    :param method: The ingestion method. Refer to IIngester for more information .
    :param target: The ingestion target. Refer to IIngester for more information .
    """

    id: str
    method: str
    target: Optional[str] = None
    # TODO: config when destination targets support being passed configs


@dataclass
class DataFlowMappingDefinition:
    """
    Defines how data flows from a source to a destination and the optional transformation in between.

    :param from_source: The source definition from where data originates.
    :param to_destination: The destination definition where data will be sent.
    :param map_function: An optional callable to transform data as it moves from source to destination.
                It accepts a payload and returns a payload or None. Returning None means skippping the payload ingestion!
    """

    from_source: SourceDefinition
    to_destination: DestinationDefinition
    map_function: Optional[
        Callable[[DataSourcePayload], Optional[DataSourcePayload]]
    ] = None
    # TODO add configuration for mappings tables and columns or function


@dataclass
class Definitions:
    """
    Aggregates all the source, destination, and flow definitions for an ingestion pipeline.

    :param sources: Dictionary of source definitions.
    :param destinations: Dictionary of destination definitions.
    :param flows: List of data flow mapping definitions.
    """

    sources: Dict[str, SourceDefinition]
    destinations: Dict[str, DestinationDefinition]
    flows: List[DataFlowMappingDefinition]
