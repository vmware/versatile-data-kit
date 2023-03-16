# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib

from vdk.internal.builtin_plugins.config.job_config import JobConfig


class ConfigFileLocator:
    """
    Locate the config.ini file
    """

    @staticmethod
    def get_config_file(directory: pathlib.Path) -> pathlib.Path | None:
        """Locates the current directory and the file in the directory that is called config.ini.
        Other files in the directory are ignored.
        :return: the file or None if the file does not exist
        :rtype: :class:`.list`
        """
        for file in directory.iterdir():
            if file.name.lower() == "config.ini":
                return file
        return None


class JobData:
    """
    class responsible for retrieving data for the job
    """

    def __init__(self):
        self._path = pathlib.Path(os.getcwd())
        self._config = JobConfig(ConfigFileLocator.get_config_file(self._path))

    def get_job_path(self) -> str:
        return str(self._path)

    def get_job_name(self) -> str:
        return os.path.basename(self._path)

    def get_team_name(self) -> str:
        return self._config.get_team()
