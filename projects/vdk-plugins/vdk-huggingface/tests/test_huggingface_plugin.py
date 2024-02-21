# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
import time

import pytest
from click.testing import Result
from huggingface_hub import HfApi
from vdk.plugin.huggingface import plugin_entry
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


@pytest.mark.skipif(
    os.environ.get("HUGGINGFACE_TOKEN") is None
    or os.environ.get("HUGGINGFACE_REPO_ID") is None,
    reason="Skipping test until HUGGINGFACE_TOKEN and HUGGINGFACE_REPO_ID and are set",
)
def test_huggingface_upload():
    runner = CliEntryBasedTestRunner(plugin_entry)

    time_var = time.time()
    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("huggingface-job"),
            "--arguments",
            json.dumps({"time": time_var}),
        ]
    )
    cli_assert_equal(0, result)

    api = HfApi()
    file_path = api.hf_hub_download(
        repo_id=os.environ["HUGGINGFACE_REPO_ID"],
        filename="test_vdk_table",
        repo_type="dataset",
    )
    row = [{"str_col": "str", "int_col": 2, "bool_col": False, "time": time_var}]
    assert json.loads(pathlib.Path(file_path).read_text()) == row * 10

    file_path = api.hf_hub_download(
        repo_id=os.environ["HUGGINGFACE_REPO_ID"],
        filename="test_vdk_table2",
        repo_type="dataset",
    )
    row = [{"str_col": "str", "int_col": 2, "bool_col": False, "time": time_var}]
    assert json.loads(pathlib.Path(file_path).read_text()) == row * 10
