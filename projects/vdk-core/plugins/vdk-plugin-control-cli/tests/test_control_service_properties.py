# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json

import pytest
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal.core.errors import PlatformServiceError
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError
from vdk.plugin.control_cli_plugin.control_service_properties import (
    ControlPlanePropertiesServiceClient,
)
from werkzeug import Request
from werkzeug import Response


def test_read_properties(httpserver: PluginHTTPServer):
    api_url = httpserver.url_for("")
    response = {"a": "b", "int_value": "1"}

    httpserver.expect_request(
        method="GET",
        uri=f"/data-jobs/for-team/test-team/name/test-job/deployments/release/properties",
    ).respond_with_json(response)
    httpserver.expect_request(
        uri=f"/data-jobs/for-team/test-team/name/empty-job/deployments/release/properties"
    ).respond_with_json({})

    url = (
        api_url
        + "/data-jobs/for-team/{team_name}/name/{job_name}/deployments/release/properties"
    )
    props = ControlPlanePropertiesServiceClient(url, "test-team")

    assert props.read_properties("test-job", "test-team") == response
    assert props.read_properties("empty-job", "test-team") == {}


def test_write_properties(httpserver: PluginHTTPServer):
    api_url = httpserver.url_for("")
    data = {"a": "b", "int_value": "1"}
    sent_data = []

    def handler(r: Request):
        sent_data.append(json.loads(r.data))
        return Response(status=204)

    httpserver.expect_request(
        method="PUT",
        uri=f"/data-jobs/for-team/test-team/name/test-job/deployments/release/properties",
    ).respond_with_handler(handler)

    url = (
        api_url
        + "/data-jobs/for-team/{team_name}/name/{job_name}/deployments/release/properties"
    )
    props = ControlPlanePropertiesServiceClient(url, "test-team")
    props.write_properties("test-job", "test-team", data)

    assert sent_data == [data]


def test_read_properties_401_error(httpserver: PluginHTTPServer):
    props = _setup_and_create_properties_client(httpserver, Response(status=401))
    with pytest.raises(VdkConfigurationError):
        props.read_properties("test-job", "test-team")


def test_read_properties_403_error(httpserver: PluginHTTPServer):
    props = _setup_and_create_properties_client(httpserver, Response(status=403))
    with pytest.raises(UserCodeError):
        props.read_properties("test-job", "test-team")


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
        uri=f"/data-jobs/for-team/test-team/name/test-job/deployments/release/properties",
    ).respond_with_response(response)
    url = (
        api_url
        + "/data-jobs/for-team/{team_name}/name/{job_name}/deployments/release/properties"
    )
    props = ControlPlanePropertiesServiceClient(url, "test-team", retries=1)
    return props
