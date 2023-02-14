# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import gzip
import sys
from decimal import Decimal
from unittest import mock
from unittest.mock import MagicMock

import pytest
import simplejson as json
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
encoding = "utf-8"


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


@mock.patch("requests.Session.post", side_effect=mocked_requests_post)
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
        url="http://example.com/data-source",
        data=json.dumps([payload]),
        headers={"Content-Type": "application/octet-stream"},
        timeout=(None, None),
        cert=None,
        verify=None,
    )


@mock.patch("requests.Session.post", side_effect=mocked_requests_post)
def test_ingest_over_http_compression(mock_post):
    def configuration_side_effect(*args, **kwargs):
        if args[0] == "INGEST_OVER_HTTP_COMPRESSION_THRESHOLD_BYTES":
            return 3
        if args[0] == "INGEST_OVER_HTTP_COMPRESSION_ENCODING":
            return encoding
        return None

    job_context = MagicMock()
    job_context.core_context.configuration.get_value.side_effect = (
        configuration_side_effect
    )
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
        data=gzip.compress(json.dumps([payload]).encode(encoding)),
        url="http://example.com/data-source",
        timeout=(None, None),
        cert=None,
        verify=None,
    )


@mock.patch("requests.Session.post", side_effect=mocked_requests_post)
def test_ingest_over_http_result(mock_post):
    def configuration_side_effect(*args, **kwargs):
        if args[0] == "INGEST_OVER_HTTP_COMPRESSION_THRESHOLD_BYTES":
            return 3
        if args[0] == "INGEST_OVER_HTTP_COMPRESSION_ENCODING":
            return encoding
        return None

    job_context = MagicMock()
    job_context.core_context.configuration.get_value.side_effect = (
        configuration_side_effect
    )
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)
    ingestion_result = http_ingester.ingest_payload(
        payload=[payload],
        destination_table="test_table",
        target="http://example.com/data-source",
    )

    assert ingestion_result["uncompressed_size_in_bytes"] == sys.getsizeof(
        json.dumps([payload])
    )
    assert ingestion_result["compressed_size_in_bytes"] == sys.getsizeof(
        gzip.compress(json.dumps([payload], allow_nan=False).encode(encoding))
    )
    assert ingestion_result["http_status"] == 200


@mock.patch("requests.Session.post", side_effect=mocked_requests_post)
def test_ingest_over_http_missing_target(mock_post):
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)
    with pytest.raises(VdkConfigurationError):
        http_ingester.ingest_payload(
            payload=[payload],
            destination_table="test_table",
        )


@mock.patch("requests.Session.post", side_effect=mocked_requests_post)
def test_ingest_over_http_missing_destination_table(mock_post):
    test_payload = [{"key1": 42, "key2": True}]
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)

    with pytest.raises(UserCodeError):
        http_ingester.ingest_payload(
            payload=test_payload, target="http://example.com/data-source"
        )


@mock.patch("requests.Session.post", side_effect=mocked_requests_post)
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


@mock.patch("requests.Session.mount")
@mock.patch("requests.Session.post", side_effect=mocked_requests_post)
def test_ingest_over_http_request_parameters_propagation(mock_post, mock_mount):
    retry_total = 10
    retry_backoff_factor = 30
    retry_status_forcelist = "500,502,503,504"
    allow_nan = False

    def configuration_side_effect(*args, **kwargs):
        def arg(a):
            return args[0] == a

        if arg("INGEST_OVER_HTTP_CONNECT_TIMEOUT_SECONDS"):
            return 10
        if arg("INGEST_OVER_HTTP_READ_TIMEOUT_SECONDS"):
            return 300
        if arg("INGEST_OVER_HTTP_VERIFY"):
            return True
        if arg("INGEST_OVER_HTTP_CERT_FILE_PATH"):
            return "cert.pem"
        if arg("INGEST_OVER_HTTP_COMPRESSION_THRESHOLD_BYTES"):
            return 3
        if arg("INGEST_OVER_HTTP_COMPRESSION_ENCODING"):
            return encoding
        if arg("INGEST_OVER_HTTP_RETRY_TOTAL"):
            return retry_total
        if arg("INGEST_OVER_HTTP_RETRY_BACKOFF_FACTOR"):
            return retry_backoff_factor
        if arg("INGEST_OVER_HTTP_RETRY_STATUS_FORCELIST"):
            return retry_status_forcelist
        if arg("INGEST_OVER_HTTP_ALLOW_NAN"):
            return allow_nan
        return None

    job_context = MagicMock()
    job_context.core_context.configuration.get_value.side_effect = (
        configuration_side_effect
    )
    IngestOverHttp(job_context).ingest_payload(
        payload=[payload],
        destination_table="test_table",
        target="http://example.com/data-source",
    )

    retries_called = mock_mount.call_args[0][1].max_retries
    assert retries_called.total == retry_total
    assert retries_called.backoff_factor == retry_backoff_factor
    assert (
        ",".join(
            [str(s) for s in mock_mount.call_args[0][1].max_retries.status_forcelist]
        )
        == retry_status_forcelist
    )

    mock_post.assert_called_with(
        url="http://example.com/data-source",
        data=gzip.compress(json.dumps([payload], allow_nan=allow_nan).encode(encoding)),
        headers={
            "Content-Type": "application/octet-stream",
            "Content-encoding": "gzip",
        },
        timeout=(10, 300),
        cert="cert.pem",
        verify=True,
    )


@mock.patch("requests.Session.post", side_effect=mocked_requests_post)
def test_ingest_over_http_special_type(mock_post):
    http_ingester: IngestOverHttp = IngestOverHttp(job_context)
    payload["decimal"] = Decimal(15.5)
    http_ingester.ingest_payload(
        payload=[payload],
        destination_table="test_table",
        target="http://example.com/data-source",
    )

    assert mock_post.call_count == 1

    payload["@table"] = "test_table"

    mock_post.assert_called_with(
        url="http://example.com/data-source",
        data=json.dumps([payload]),
        headers={"Content-Type": "application/octet-stream"},
        timeout=(None, None),
        cert=None,
        verify=None,
    )


@mock.patch("simplejson.dumps")
def test_ingest_over_http_json_dumps_parameters_propagation(mock_jsondumps):
    allow_nan = True

    def configuration_side_effect(*args, **kwargs):
        def arg(a):
            return args[0] == a

        if arg("INGEST_OVER_HTTP_ALLOW_NAN"):
            return allow_nan
        return None

    job_context = MagicMock()
    job_context.core_context.configuration.get_value.side_effect = (
        configuration_side_effect
    )
    try:
        IngestOverHttp(job_context).ingest_payload(
            payload=[payload],
            destination_table="test_table",
            target="http://example.com/data-source",
        )
    except:
        pass

    mock_jsondumps.assert_called_with([payload], allow_nan=allow_nan)
