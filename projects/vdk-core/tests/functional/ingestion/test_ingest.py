# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass
from typing import List
from typing import Optional

from click.testing import Result
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


class IngestIntoMemoryPlugin(IIngesterPlugin):
    @dataclass
    class Payload:
        payload: List[dict]
        destination_table: Optional[str]
        target: Optional[str]
        collection_id: Optional[str]

    def __init__(self, method_name: str):
        super().__init__()
        self.payloads: List[IngestIntoMemoryPlugin.Payload] = []
        self.method_name = method_name

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ):
        self.payloads.append(
            IngestIntoMemoryPlugin.Payload(
                payload, destination_table, target, collection_id
            )
        )

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.ingester.add_ingester_factory_method(self.method_name, lambda: self)


def test_ingest_multiple_methods():
    ingest_plugin = IngestIntoMemoryPlugin("memory")
    ingest_plugin2 = IngestIntoMemoryPlugin("memory2")
    runner = CliEntryBasedTestRunner(ingest_plugin, ingest_plugin2)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("test-ingest-multiple-methods-job")]
    )

    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) == 20
    assert len(ingest_plugin2.payloads) == 20
