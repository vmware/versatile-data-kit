# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib


class ConfigFileLocator:
    """
    Locate the config.ini dile
    """

    @staticmethod
    def get_config_file() -> pathlib.Path | None:
        """Locates the current directory and the file in the directory that is called config.ini.
        Other files in the directory are ignored.
        :return: the file or None if the file does not exist
        :rtype: :class:`.list`
        """
        directory = pathlib.Path(os.getcwd())
        for file in directory.iterdir():
            if file.name.lower() == "config.ini":
                return file
        return None
