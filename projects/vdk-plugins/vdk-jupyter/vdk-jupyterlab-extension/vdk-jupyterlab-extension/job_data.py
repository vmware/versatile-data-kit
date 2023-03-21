# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib

from vdk.internal.builtin_plugins.config.job_config import JobConfig


class JobDataLoader:
    """
    Class responsible for retrieving data for the job of the provided directory
    """

    def __init__(self, working_directory: str):
        self._path = pathlib.Path(os.getcwd() + "/" + working_directory)
        self._config = JobConfig(self._path)

    def get_job_path(self) -> str:
        return str(self._path)

    def get_job_name(self) -> str:
        return os.path.basename(self._path)

    def get_team_name(self) -> str:
        if self._config:
            return self._config.get_team()
        return ""
