# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from threading import RLock
from typing import Dict
from typing import List
from typing import Optional

from huggingface_hub import CommitOperationAdd
from huggingface_hub import HfApi
from vdk.api.plugin.plugin_input import IIngesterPlugin


@dataclass(frozen=True)
class OpKey:
    repo_id: str
    destination_table: str


class IngestToHuggingface(IIngesterPlugin):
    def __init__(self, repo_id: str):
        self._api = HfApi()
        self._repo_id = repo_id
        self._file_handles: Dict[OpKey, any] = {}
        self._locks: Dict[OpKey, RLock] = defaultdict(RLock)

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ) -> Optional[IIngesterPlugin.IngestionMetadata]:
        repo_id = target if target is not None else self._repo_id

        op_key = OpKey(repo_id, destination_table)
        with self._locks[op_key]:
            if op_key not in self._file_handles:
                self._check_and_create_repo(repo_id)
                temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
                self._file_handles[op_key] = temp_file

            self._append_payload(op_key, payload)

        return None

    def _append_payload(self, op_key: OpKey, payload: List[Dict]):
        temp_file = self._file_handles[op_key]
        temp_file.flush()
        temp_file.seek(0)
        existing_data_str = temp_file.read()

        existing_data = json.loads(existing_data_str) if existing_data_str else []

        merged_data = existing_data + payload
        temp_file.seek(0)
        temp_file.truncate()
        json.dump(merged_data, temp_file)

    def commit_all(self):
        for op_key, temp_file in self._file_handles.items():
            with self._locks[op_key]:
                temp_file.close()
                addition = CommitOperationAdd(
                    path_in_repo=op_key.destination_table,
                    path_or_fileobj=temp_file.name,
                )
                self._api.preupload_lfs_files(
                    op_key.repo_id, additions=[addition], repo_type="dataset"
                )
                self._api.create_commit(
                    op_key.repo_id,
                    operations=[addition],
                    repo_type="dataset",
                    commit_message="Automatic commit by vdk-huggingface",
                )
                os.unlink(temp_file.name)
        self._file_handles.clear()

    def _check_and_create_repo(self, repo_id: str):
        if not self._api.repo_exists(repo_id):
            self._api.create_repo(repo_id=repo_id, exist_ok=True, repo_type="dataset")
