# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json


async def test_get_example(jp_fetch):
    # When
    response = await jp_fetch("vdk-jupyterlab-extension", "get_example")

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "data": "This is /vdk-jupyterlab-extension/get_example endpoint!"
    }
