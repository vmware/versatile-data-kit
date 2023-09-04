# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import shutil
import tempfile
from pathlib import Path

import pytest
from vdk_jupyterlab_extension.jupyter_notebook import clear_notebook_outputs


@pytest.fixture(scope="function", autouse=True)
def create_temporary_directory():
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir.name
    temp_dir.cleanup()


@pytest.mark.parametrize("job_dir", ["ingest-notebook"])
def test_notebook_output_cleaner(job_dir, create_temporary_directory):
    base_dir = Path(__file__).parent / "data"
    dir_path = base_dir / job_dir
    temp_dir = create_temporary_directory

    for notebook_path in dir_path.glob("*.ipynb"):
        temp_notebook_path = Path(temp_dir) / notebook_path.name
        shutil.copy2(notebook_path, temp_notebook_path)
        clear_notebook_outputs(str(temp_notebook_path))

    for notebook_path in dir_path.glob("*.ipynb"):
        temp_notebook_path = Path(temp_dir) / notebook_path.name
        with temp_notebook_path.open("r") as f:
            content = json.load(f)
        for cell in content["cells"]:
            if cell["cell_type"] == "code":
                assert cell["execution_count"] is None
                assert not cell["outputs"]
