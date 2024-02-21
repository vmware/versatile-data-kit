# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import tempfile
from typing import Iterator
from typing import List
from typing import Optional

from dulwich import porcelain
from vdk.plugin.data_source_git.utils import detect_language
from vdk.plugin.data_source_git.utils import is_test_file
from vdk.plugin.data_sources.config import config_class
from vdk.plugin.data_sources.config import config_field
from vdk.plugin.data_sources.data_source import DataSourcePayload
from vdk.plugin.data_sources.data_source import IDataSource
from vdk.plugin.data_sources.data_source import (
    IDataSourceConfiguration,
)
from vdk.plugin.data_sources.data_source import IDataSourceStream
from vdk.plugin.data_sources.factory import data_source
from vdk.plugin.data_sources.state import IDataSourceState

DESCRIPTION = """Git data source.
Extract content from Git repositories and associated file metadata.
"""


@config_class(name="git", description=DESCRIPTION)
class GitDataSourceConfiguration(IDataSourceConfiguration):
    git_url: str = config_field(description="Git URL that would be cloned. ")
    git_ssh_key: Optional[str] = config_field(
        description="SSH key to use when cloning the repo."
        "Leave empty if no authentication is needed",
        default="",
    )


@data_source(name="git", config_class=GitDataSourceConfiguration)
class GitDataSource(IDataSource):
    """
    Data source who is only generating some dummy data for testing purposes.
    """

    def __init__(self):
        self._config = None
        self._streams = []

    def configure(self, config: GitDataSourceConfiguration):
        self._config = config

    def connect(self, state: IDataSourceState):
        if not self._streams:
            self._streams = [GitDataSourceStream(self._config.git_url)]

    def disconnect(self):
        self._streams = []

    def streams(self) -> List[IDataSourceStream]:
        return self._streams


class GitDataSourceStream(IDataSourceStream):
    """ """

    def name(self) -> str:
        return self._url

    def __init__(self, url: str):
        self._url = url

    def read(self) -> Iterator[DataSourcePayload]:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = porcelain.clone(source=self._url, target=tmp_dir, depth=1)

            for path, entry in repo.open_index().items():
                file_path = path.decode("utf-8")
                blob = repo.get_object(entry.sha)
                # TODO: VDK send_object/tabular_data for ingestion doesn't support bytes so we convert it for now.
                data = blob.data.decode("utf-8")
                metadata = {
                    "size": len(data),
                    "path": file_path,
                    "num_lines": data.count("\n") + 1,
                    "file_extension": os.path.splitext(file_path)[1],
                    "programming_language": detect_language(file_path),
                    "is_likely_test_file": is_test_file(file_path),
                }
                yield DataSourcePayload({"content": data}, metadata=metadata)
