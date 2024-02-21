# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from typing import Dict
from typing import TypeVar

import toml
from vdk.plugin.data_sources.mapping.definitions import DataFlowMappingDefinition
from vdk.plugin.data_sources.mapping.definitions import Definitions
from vdk.plugin.data_sources.mapping.definitions import DestinationDefinition
from vdk.plugin.data_sources.mapping.definitions import SourceDefinition

T = TypeVar("T")


def definitions_from_dict(data: Dict) -> Definitions:
    sources = {
        k: SourceDefinition(id=k, **v) for k, v in data.get("sources", {}).items()
    }
    destinations = {
        k: DestinationDefinition(id=k, **v)
        for k, v in data.get("destinations", {}).items()
    }
    flows_list = []
    for flow in data.get("flows", []):
        if flow["from"] not in sources:
            raise ValueError(
                f"Data source {flow['from']} is not defined and cannot be used in a flow.\n"
                f"Please define it first in the [sources] section of the configuration.\n"
                f"Currenty defined surces: {list(sources.keys())}"
            )
        if flow["to"] not in destinations:
            raise ValueError(
                f"Data destination {flow['to']} is not defined and cannot be used in a flow.\n"
                f"Please define it first in the [destinations] section of the configuration.\n"
                f"Currenty defined destinations: {list(destinations.keys())}"
            )

        flow_obj = DataFlowMappingDefinition(
            from_source=sources[flow["from"]], to_destination=destinations[flow["to"]]
        )
        flows_list.append(flow_obj)

    return Definitions(sources=sources, destinations=destinations, flows=flows_list)


def load_config(file_path: str) -> Definitions:
    parsed_toml = toml.load(file_path)
    return definitions_from_dict(parsed_toml)
