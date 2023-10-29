# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import toml
from vdk.plugin.data_sources.mapping.definitions import DataFlowMappingDefinition
from vdk.plugin.data_sources.mapping.definitions import Definitions
from vdk.plugin.data_sources.mapping.definitions import DestinationDefinition
from vdk.plugin.data_sources.mapping.definitions import SourceDefinition
from vdk.plugin.data_sources.mapping.toml_parser import definitions_from_dict


def write_tmp_toml(tmp_path, content):
    p = tmp_path / "config.toml"
    p.write_text(content)
    return p


def test_empty_toml_file(tmp_path):
    p = write_tmp_toml(tmp_path, "")
    parsed_toml = toml.load(p)
    assert definitions_from_dict(parsed_toml) == Definitions({}, {}, [])


def sample_toml_data():
    return """
    [sources.source1]
    name = "source_one"
    config = { key = "value" }

    [sources.source2]
    name = "source_two"
    config = { key = "value2" }

    [destinations.dest1]
    method = "POST"
    target = "target_one"

    [destinations.dest2]
    method = "GET"
    target = "target_two"

    [[flows]]
    from="source1"
    to="dest1"
    [[flows]]
    from="source2"
    to="dest2"
    """


def get_expected():
    s1 = SourceDefinition("source1", "source_one", {"key": "value"})
    s2 = SourceDefinition("source2", "source_two", {"key": "value2"})
    d1 = DestinationDefinition("dest1", "POST", "target_one")
    d2 = DestinationDefinition("dest2", "GET", "target_two")
    return Definitions(
        sources={
            "source1": s1,
            "source2": s2,
        },
        destinations={
            "dest1": d1,
            "dest2": d2,
        },
        flows=[DataFlowMappingDefinition(s1, d1), DataFlowMappingDefinition(s2, d2)],
    )


def test_load_config_ingest_definitions(tmp_path):
    p = write_tmp_toml(tmp_path, sample_toml_data())
    parsed_toml = toml.load(p)
    assert definitions_from_dict(parsed_toml) == get_expected()


def test_only_sources(tmp_path):
    data = """
    sources.source1.name = "source_one"
    sources.source1.config = { key = "value" }
    """
    p = write_tmp_toml(tmp_path, data)
    parsed_toml = toml.load(p)
    expected = Definitions(
        sources={
            "source1": SourceDefinition("source1", "source_one", {"key": "value"})
        },
        destinations={},
        flows=[],
    )
    assert definitions_from_dict(parsed_toml) == expected
