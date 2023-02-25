# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from unittest import mock

import pytest
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal.core.errors import PlatformServiceError
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError
from vdk.plugin.control_cli_plugin.control_service_properties_client import (
    ControlServicePropertiesServiceClient,
)
from werkzeug import Request
from werkzeug import Response


@mock.patch.dict(os.environ, {"VDK_CONTROL_HTTP_TOTAL_RETRIES": "1"})
def test_read_properties(httpserver: PluginHTTPServer):
    api_url = httpserver.url_for("")
    response = {"a": "b", "int_value": "1"}

    httpserver.expect_request(
        method="GET",
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments/TODO/properties",
    ).respond_with_json(response)
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/empty-job/deployments/TODO/properties"
    ).respond_with_json({})

    props = ControlServicePropertiesServiceClient(api_url)

    assert props.read_properties("test-job", "test-team") == response
    assert props.read_properties("empty-job", "test-team") == {}


@mock.patch.dict(os.environ, {"VDK_CONTROL_HTTP_TOTAL_RETRIES": "1"})
def test_write_properties(httpserver: PluginHTTPServer):
    api_url = httpserver.url_for("")
    data = {"a": "b", "int_value": "1"}
    sent_data = []

    def handler(r: Request):
        sent_data.append(json.loads(r.data))
        return Response(status=204)

    httpserver.expect_request(
        method="PUT",
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments/TODO/properties",
    ).respond_with_handler(handler)

    props = ControlServicePropertiesServiceClient(api_url)
    props.write_properties("test-job", "test-team", data)

    assert sent_data == [data]


@mock.patch.dict(os.environ, {"VDK_CONTROL_HTTP_TOTAL_RETRIES": "1"})
def test_read_properties_401_error(httpserver: PluginHTTPServer):
    props = _setup_and_create_properties_client(httpserver, Response(status=401))
    with pytest.raises(VdkConfigurationError):
        props.read_properties("test-job", "test-team")


@mock.patch.dict(os.environ, {"VDK_CONTROL_HTTP_TOTAL_RETRIES": "1"})
def test_read_properties_403_error(httpserver: PluginHTTPServer):
    props = _setup_and_create_properties_client(httpserver, Response(status=403))
    with pytest.raises(UserCodeError):
        props.read_properties("test-job", "test-team")


@mock.patch.dict(os.environ, {"VDK_CONTROL_HTTP_TOTAL_RETRIES": "1"})
def test_read_properties_500_error(httpserver: PluginHTTPServer):
    props = _setup_and_create_properties_client(httpserver, Response(status=500))
    with pytest.raises(PlatformServiceError):
        props.read_properties("test-job", "test-team")


def _setup_and_create_properties_client(
    httpserver: PluginHTTPServer, response: Response
):
    api_url = httpserver.url_for("")
    httpserver.expect_request(
        method="GET",
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments/TODO/properties",
    ).respond_with_response(response)
    props = ControlServicePropertiesServiceClient(api_url)
    return props
