# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json


async def test_run_job_get(jp_fetch):
    # When
    response = await jp_fetch("vdk-jupyterlab-extension", "run", method="GET")

    # Then
    assert response.code == 200


async def test_run_job_post(jp_fetch):
    # When
    body = {"jobPath": "", "jobArguments": ""}
    response = await jp_fetch(
        "vdk-jupyterlab-extension", "run", method="POST", body=json.dumps(body)
    )

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {"message": "0"}


async def test_delete_job_post(jp_fetch):
    # When
    body = {"jobName": "", "jobTeam": "", "restApiUrl": ""}
    response = await jp_fetch(
        "vdk-jupyterlab-extension", "delete", method="POST", body=json.dumps(body)
    )

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "error": "true",
        "message": "¯\\_(ツ)_/¯\n"
        "\n"
        "what: Control Service Error\n"
        "why: No host specified.\n"
        "consequences: Operation cannot complete.\n"
        "countermeasures: Verify that the provided url (--rest-api-url) is "
        "valid and points to the correct host.\n",
    }


async def test_download_job_post(jp_fetch):
    # When
    body = {"jobName": "", "jobTeam": "", "restApiUrl": "", "parentPath": ""}
    response = await jp_fetch(
        "vdk-jupyterlab-extension", "download", method="POST", body=json.dumps(body)
    )

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "error": "true",
        "message": "¯\\_(ツ)_/¯\n"
        "\n"
        "what: Control Service Error\n"
        "why: No host specified.\n"
        "consequences: Operation cannot complete.\n"
        "countermeasures: Verify that the provided url (--rest-api-url) is "
        "valid and points to the correct host.\n",
    }


async def test_create_job_post(jp_fetch):
    # When
    body = {
        "jobName": "",
        "jobTeam": "",
        "restApiUrl": "",
        "jobPath": "",
        "isLocal": "",
        "isCloud": "",
    }
    response = await jp_fetch(
        "vdk-jupyterlab-extension", "create", method="POST", body=json.dumps(body)
    )

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "error": "true",
        "message": "¯\\_(ツ)_/¯\n"
        "\n"
        "what: Cannot create job with name: .\n"
        "why: Job name must only contain alphanumerical symbols and "
        "dashes.\n"
        "consequences: Cannot create the new job.\n"
        "countermeasures: Ensure that the job name is between 5 and 45 "
        "characters long, that it contains only alphanumeric characters "
        "and dashes, that it contains no uppercase characters, and that it "
        "begins with a letter.\n",
    }
