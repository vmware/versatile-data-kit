# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import re

import pytest
from atlassian import Confluence
from click.testing import Result
from vdk.plugin.confluence_data_source import plugin_entry
from vdk.plugin.confluence_data_source.data_source import PageContentStream
from vdk.plugin.data_sources import plugin_entry as data_sources_plugin_entry
from vdk.plugin.data_sources.data_source import DataSourcePayload
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


@pytest.fixture
def mock_confluence_api(requests_mock):
    space_key = "SPACE_KEY"
    base_url = r"https://your-confluence-instance\.atlassian\.net/wiki/rest/api/content"

    def request_matcher(request, context):
        start = int(request.qs.get("start", ["0"])[0])
        limit = int(request.qs.get("limit", ["50"])[0])

        total_pages = 150
        next_start = start + limit

        if start >= total_pages:
            # simulate the end of pagination by returning an empty results list
            return {"results": [], "start": start, "limit": limit, "size": 0}

        results = []
        for i in range(start, min(start + limit, total_pages)):
            results.append(
                {
                    "id": str(123 + i),
                    "title": f"Test Page {i}",
                    "body": {"storage": {"value": f"<p>Hello World from page {i}</p>"}},
                    "version": {"number": 1},
                    "history": {"lastUpdated": {"when": "2021-01-01T00:00:00.000Z"}},
                }
            )

        mock_response = {
            "results": results,
            "start": start,
            "limit": limit,
            "size": len(results),
        }
        if next_start < total_pages:
            mock_response["_links"] = {
                "next": f"{base_url}?spaceKey={space_key}&start={next_start}&limit={limit}&expand=body.storage,version,history.lastUpdated"
            }

        return mock_response

    pattern = re.compile(base_url + r"\?.*spaceKey=" + space_key + ".*")
    requests_mock.get(pattern, json=request_matcher)


@pytest.mark.usefixtures("mock_confluence_api")
def test_page_content_stream():
    confluence = Confluence(
        url="https://your-confluence-instance.atlassian.net/wiki", token="token"
    )
    stream = PageContentStream(confluence_client=confluence, space_key="SPACE_KEY")
    pages = list(stream.read())
    assert len(pages) > 0
    for page in pages:
        assert isinstance(page, DataSourcePayload)
        assert page.metadata["space_key"] == "SPACE_KEY"
        assert "existing" in page.metadata["status"]


@pytest.mark.usefixtures("mock_confluence_api")
def test_run_api_ingest(tmpdir):
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(
        ingest_plugin, data_sources_plugin_entry, plugin_entry
    )
    source_configuration = {
        "confluence_url": "https://your-confluence-instance.atlassian.net/wiki",
        "api_token": "token",
        "space_key": "SPACE_KEY",
        "cloud": True,
        "confluence_kwargs": {},
        "username": None,
        "personal_access_token": None,
        "oauth2": None,
    }

    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("ingest-test-job"),
            "--arguments",
            json.dumps({"config": source_configuration}),
        ]
    )

    cli_assert_equal(0, result)
    payload_objects = ingest_plugin.payloads
    expected_payload_objects = get_expected_data()

    all_raw_contents = [
        item["raw_content"]
        for payload_object in payload_objects
        for item in payload_object.payload
    ]
    expected_contents = [
        item["raw_content"]
        for expected_payload_object in expected_payload_objects
        for item in expected_payload_object.payload
    ]

    for content, expected_content in zip(all_raw_contents, expected_contents):
        assert (
            content == expected_content
        ), f"Content {content} does not match expected content {expected_content}"


def get_expected_data():
    example_payloads = []
    for i in range(150):
        example_payloads.append({"raw_content": f"<p>Hello World from page {i}</p>"})

    expected_payloads = [
        IngestIntoMemoryPlugin.Payload(
            payload=example_payloads,
            destination_table="confluence-space-SPACE_KEY-page-content",
            target=None,
            collection_id=None,
        )
    ]
    return expected_payloads
