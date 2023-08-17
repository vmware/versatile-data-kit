# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import shutil
from pathlib import Path

import pytest
from vdk_jupyterlab_extension.jupyter_notebook import NotebookJobDirectory


@pytest.fixture(scope="module", autouse=True)
def backup_and_restore_notebooks():
    base_dir = Path(__file__).parent / "jobs"
    backup_dir = Path(__file__).parent / "jobs_backup"

    # Backup the original directories
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    shutil.copytree(base_dir, backup_dir)

    yield  # pause the fixture until the test completes

    # Restore the directories after the test
    shutil.rmtree(base_dir)
    shutil.copytree(backup_dir, base_dir)
    shutil.rmtree(backup_dir)


@pytest.mark.parametrize("job_dir", ["ingest-job", "mixed-job"])
def test_remove_outputs(job_dir):
    base_dir = Path(__file__).parent / "jobs"
    dir_path = base_dir / job_dir

    job = NotebookJobDirectory(dir_path)
    job.remove_outputs_from_all()

    # Verify outputs have been removed from the notebook files
    for notebook_path in dir_path.glob("*.ipynb"):
        with notebook_path.open("r") as f:
            content = json.load(f)
        for cell in content["cells"]:
            if cell["cell_type"] == "code":
                assert cell["execution_count"] is None
                assert not cell["outputs"]
