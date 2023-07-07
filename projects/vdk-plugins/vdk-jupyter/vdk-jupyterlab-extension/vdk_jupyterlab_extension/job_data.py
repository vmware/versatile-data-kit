# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib

from vdk.internal.builtin_plugins.config.job_config import JobConfig


class JobDataLoader:
    """
      The JobDataLoader class is used for retrieving job-specific data from a provided directory.
    Attributes:
        _path (Path): A Path object representing the path to the job's directory.
        _config (JobConfig): A JobConfig object used to access job configuration data.
    Methods:
        get_job_path(): Returns the absolute path of the job directory as a string.
        get_job_name(): Returns the name of the job.
        get_team_name(): Returns the team name associated with the job.
    """

    def __init__(self, working_directory: str):
        self._path = pathlib.Path(os.getcwd() + "/" + working_directory)
        if not os.path.isdir(self._path):
            raise ValueError(f"{self._path} is not a valid directory.")
        self._config = JobConfig(self._path)

    def get_job_path(self) -> str:
        return str(self._path)

    def get_job_name(self) -> str:
        return os.path.basename(self._path)

    def get_team_name(self) -> str:
        if self._config:
            return self._config.get_team()
        return ""
