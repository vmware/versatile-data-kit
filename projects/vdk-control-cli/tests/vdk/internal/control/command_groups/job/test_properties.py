# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import pathlib
from typing import List

from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal import test_utils
from vdk.internal.control.command_groups.job.properties import properties_command
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response

test_utils.disable_vdk_authentication()

team_name = "test-team"
job_name = "test-job"
deployment_id = "TODO"


def _run_properties_command(rest_api_url: str, args: List[str], input=None):
    runner = CliRunner()
    result = runner.invoke(
        properties_command,
        args + ["-n", "test-job"] + ["-t", "test-team"] + ["-u", rest_api_url],
        input=input,
    )
    return result


def test_properties_list_empty(httpserver: PluginHTTPServer):
    rest_api_url = httpserver.url_for("")

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/{deployment_id}/properties"
    ).respond_with_json({})

    result = _run_properties_command(rest_api_url, ["--list", "-o", "json"])
    test_utils.assert_click_status(result, 0)
    assert result.output.strip() == "{}"


def test_properties_list(httpserver: PluginHTTPServer):
    rest_api_url = httpserver.url_for("")

    # TODO:
    # response = {"a": "b", "nested": {"inner": "inner_value"}, "int_value": 1}
    response = {"aaaaa": "bbbbb", "nested": {"inner": "inner_value"}, "int_value": "1"}

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/{deployment_id}/properties"
    ).respond_with_json(response)

    result = _run_properties_command(rest_api_url, ["--list", "-o", "json"])
    test_utils.assert_click_status(result, 0)
    assert json.loads(result.output) == response

    result = _run_properties_command(rest_api_url, ["--list", "-o", "text"])
    test_utils.assert_click_status(result, 0)
    # we do not impose strict contact on the table presentaiton
    # we just verify the value on the expected row.
    assert "aaaaa" in str(result.output).splitlines()[2]
    assert "nested" in str(result.output).splitlines()[3]
    assert "int_value" in str(result.output).splitlines()[4]


def test_properties_get_set(httpserver: PluginHTTPServer):
    rest_api_url = _mock_properties_server(httpserver)

    result = _run_properties_command(rest_api_url, ["--set", "my-key", "my-value"])
    test_utils.assert_click_status(result, 0)

    result = _run_properties_command(rest_api_url, ["--get", "my-key", "-o", "json"])
    test_utils.assert_click_status(result, 0)
    assert result.output.strip() == '{"my-key": "my-value"}'


def test_properties_get_set_secret(httpserver: PluginHTTPServer):
    rest_api_url = _mock_properties_server(httpserver)

    result = _run_properties_command(
        rest_api_url, ["--set-secret", "secret"], input="my-secret-value"
    )
    test_utils.assert_click_status(result, 0)

    result = _run_properties_command(rest_api_url, ["--get", "secret", "-o", "json"])
    test_utils.assert_click_status(result, 0)
    assert result.output.strip() == '{"secret": "my-secret-value"}'


def test_properties_get_set_multiple(httpserver: PluginHTTPServer):
    rest_api_url = _mock_properties_server(httpserver)

    result = _run_properties_command(rest_api_url, ["--set", "key_1", "value-1"])
    test_utils.assert_click_status(result, 0)

    result = _run_properties_command(
        rest_api_url,
        ["--set", "key_2", "value-2"]
        + ["--set", "key_3", "value-3"]
        + ["--set", "", "empty"]
        + ["--set", "empty_value", ""],
    )
    test_utils.assert_click_status(result, 0)

    result = _run_properties_command(rest_api_url, ["--list", "-o", "json"])
    test_utils.assert_click_status(result, 0)
    assert (
        result.output.strip()
        == '{"key_1": "value-1", "key_2": "value-2", "key_3": "value-3", "": "empty", "empty_value": ""}'
    )


def test_properties_get_set_preserve_value_types(httpserver: PluginHTTPServer):
    rest_api_url = _mock_properties_server(
        httpserver,
        {
            "key_str": "string_value",
            "key_int": 123,
            "key_float": 3.1415,
            "key_bool": True,
        },
    )

    result = _run_properties_command(
        rest_api_url,
        ["--set", "key_str", "new_string_value"]
        + ["--set", "key_int", "456"]
        + ["--set", "key_float", "6.2831"]
        + ["--set", "key_bool", "False"],
    )
    test_utils.assert_click_status(result, 0)

    result = _run_properties_command(rest_api_url, ["--list", "-o", "json"])
    test_utils.assert_click_status(result, 0)
    assert (
        result.output.strip()
        == '{"key_str": "new_string_value", "key_int": 456, "key_float": 6.2831, "key_bool": false}'
    )

    result = _run_properties_command(
        rest_api_url, ["--set", "key_int", "string_value_cannot_be_cast_to_int"]
    )
    # we fail because we cannot cast to int
    test_utils.assert_click_status(result, 2)


def test_properties_get_set_preserve_value_types_list_dict(
    httpserver: PluginHTTPServer,
):
    rest_api_url = _mock_properties_server(
        httpserver,
        {"key_list": ["a", "b", "c"], "key_dict": dict(a="b")},
    )

    result = _run_properties_command(rest_api_url, ["--set", "key_list", "not,a,list"])
    test_utils.assert_click_status(result, 2)

    result = _run_properties_command(rest_api_url, ["--set", "key_dict", "not_a:dict"])
    test_utils.assert_click_status(result, 2)


def test_properties_delete(httpserver: PluginHTTPServer):
    rest_api_url = _mock_properties_server(
        httpserver, {"key1": "value1", "key2": "value2", "key3": 3}
    )

    result = _run_properties_command(
        rest_api_url, ["--delete", "key1", "--delete", "key3"]
    )
    test_utils.assert_click_status(result, 0)

    result = _run_properties_command(rest_api_url, ["--list", "-o", "json"])
    test_utils.assert_click_status(result, 0)
    assert result.output.strip() == '{"key2": "value2"}'


def test_properties_get_set_lots_of_values(httpserver: PluginHTTPServer):
    rest_api_url = _mock_properties_server(
        httpserver,
        {str(i): i for i in range(1, 1000)},
    )

    result = _run_properties_command(
        rest_api_url, ["--set", "key_str", "new_string_value"] + ["--set", "foo", "456"]
    )
    test_utils.assert_click_status(result, 0)

    result = _run_properties_command(rest_api_url, ["--list", "-o", "json"])
    test_utils.assert_click_status(result, 0)


def test_properties_delete_all(httpserver: PluginHTTPServer):
    rest_api_url = _mock_properties_server(
        httpserver, {"key1": "value1", "key2": "value2", "key3": 3}
    )

    result = _run_properties_command(rest_api_url, ["--delete-all-job-properties"])
    test_utils.assert_click_status(result, 0)

    result = _run_properties_command(rest_api_url, ["--list", "-o", "json"])
    test_utils.assert_click_status(result, 0)
    assert result.output.strip() == "{}"


def test_properties_overwrite_all(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = _mock_properties_server(
        httpserver, {"key1": "value1", "key2": "value2", "key3": 3}
    )

    temp_file = pathlib.Path(tmpdir).joinpath("temp-file.json")
    new_json = {"new_key": 1, "new_new_key": "new_value"}
    temp_file.write_text(json.dumps(new_json))

    result = _run_properties_command(
        rest_api_url, ["--overwrite-all-job-properties", str(temp_file)]
    )
    test_utils.assert_click_status(result, 0)

    result = _run_properties_command(rest_api_url, ["--list", "-o", "json"])
    test_utils.assert_click_status(result, 0)
    assert result.output.strip() == json.dumps(new_json)


def test_properties_overwrite_all_not_valid_josn(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    rest_api_url = _mock_properties_server(
        httpserver, {"key1": "value1", "key2": "value2", "key3": 3}
    )

    temp_file = pathlib.Path(tmpdir).joinpath("temp-file.json")
    temp_file.write_text("{not-valid-josn;}")

    result = _run_properties_command(
        rest_api_url, ["--overwrite-all-job-properties", str(temp_file)]
    )
    test_utils.assert_click_status(result, 2)


def _mock_properties_server(httpserver, initial_properties=None):
    rest_api_url = httpserver.url_for("")
    properties_cache = {
        job_name: json.dumps(initial_properties) if initial_properties else "{}"
    }

    def save_properties(r: Request):
        job_name = r.path.split("/")[5]
        properties_cache[job_name] = r.data
        return Response(status=200)

    def get_properties(r: Request):
        job_name = r.path.split("/")[5]
        data = properties_cache.get(job_name, "{}")
        return Response(data, 200, content_type="application/json")

    httpserver.expect_request(
        method="PUT",
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/{deployment_id}/properties",
    ).respond_with_handler(save_properties)
    httpserver.expect_request(
        method="GET",
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/{deployment_id}/properties",
    ).respond_with_handler(get_properties)
    return rest_api_url
