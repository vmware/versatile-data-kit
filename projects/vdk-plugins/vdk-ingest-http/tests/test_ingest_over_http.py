# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import gzip
import json
import sys
from unittest import mock
from unittest.mock import MagicMock

import pytest
from vdk.internal.core.errors import PlatformServiceError
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError
from vdk.plugin.ingest_http.ingest_over_http import IngestOverHttp

payload: dict = {
    "@id": "test_id",
    "some_data": "some_test_data",
}
job_context = MagicMock()
job_context.core_context.configuration.get_value.return_value = None


def mocked_requests_post(url, *args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.text = ""

        def json(self):
            return self.json_data

    if url == "http://example.com/data-source":
        return MockResponse(payload, 200)
    elif url == "http://example.com/wrong/data-source":
        return MockResponse(None, 500)

    return MockResponse(None, 404)


@mock.patch("requests.post", side_effect=mocked_requests_post)
def test_ingest_over_http(mock_post):
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)
    http_ingester.ingest_payload(
        payload=[payload],
        destination_table="test_table",
        target="http://example.com/data-source",
    )

    assert mock_post.call_count == 1

    payload["@table"] = "test_table"

    mock_post.assert_called_with(
        headers={"Content-Type": "application/octet-stream"},
        json=[payload],
        url="http://example.com/data-source",
        verify=False,
    )


@mock.patch("requests.post", side_effect=mocked_requests_post)
def test_ingest_over_http_compression(mock_post):
    threshold_bytes = 3
    encoding = "utf-8"
    job_context = MagicMock()
    job_context.core_context.configuration.get_value.side_effect = [
        threshold_bytes,
        encoding,
    ]
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)
    http_ingester.ingest_payload(
        payload=[payload],
        destination_table="test_table",
        target="http://example.com/data-source",
    )

    assert mock_post.call_count == 1
    payload["@table"] = "test_table"

    mock_post.assert_called_with(
        headers={
            "Content-Type": "application/octet-stream",
            "Content-encoding": "gzip",
        },
        json=gzip.compress(json.dumps([payload]).encode(encoding)),
        url="http://example.com/data-source",
        verify=False,
    )


@mock.patch("requests.post", side_effect=mocked_requests_post)
def test_ingest_over_http_result(mock_post):
    threshold_bytes = 3
    encoding = "utf-8"
    job_context = MagicMock()
    job_context.core_context.configuration.get_value.side_effect = [
        threshold_bytes,
        encoding,
    ]
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)
    ingestion_result = http_ingester.ingest_payload(
        payload=[payload],
        destination_table="test_table",
        target="http://example.com/data-source",
    )

    assert ingestion_result["uncompressed_size_in_bytes"] == sys.getsizeof([payload])
    assert ingestion_result["compressed_size_in_bytes"] == sys.getsizeof(
        gzip.compress(json.dumps([payload]).encode(encoding))
    )
    assert ingestion_result["http_status"] == 200


@mock.patch("requests.post", side_effect=mocked_requests_post)
def test_ingest_over_http_missing_target(mock_post):
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)
    with pytest.raises(VdkConfigurationError):
        http_ingester.ingest_payload(
            payload=[payload],
            destination_table="test_table",
        )


@mock.patch("requests.post", side_effect=mocked_requests_post)
def test_ingest_over_http_missing_destination_table(mock_post):
    test_payload = [{"key1": 42, "key2": True}]
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)

    with pytest.raises(UserCodeError):
        http_ingester.ingest_payload(
            payload=test_payload, target="http://example.com/data-source"
        )


@mock.patch("requests.post", side_effect=mocked_requests_post)
def test_ingest_over_http_request_errors(mock_post):
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)
    with pytest.raises(UserCodeError):
        http_ingester.ingest_payload(
            payload=[payload],
            destination_table="test_table",
            target="http://example.com/",
        )

    with pytest.raises(PlatformServiceError):
        http_ingester.ingest_payload(
            payload=[payload],
            destination_table="test_table",
            target="http://example.com/wrong/data-source",
        )
