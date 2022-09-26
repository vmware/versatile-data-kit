# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from configparser import ConfigParser
from typing import Dict

from vdk.api.plugin.plugin_input import IPropertiesServiceClient

log = logging.getLogger(__name__)


class FileSystemPropertiesServiceClient(IPropertiesServiceClient):
    """
    Implementation of IProperties that are kept on local FS only. Stateless.
    A single properties file store, supporting multiple teams and data jobs properties,
    via placing the key-values in a dedicated team and job name section to deduplicate.
    """

    def __init__(self, directory: str, filename: str):
        self._file_path = os.path.join(directory, filename)

    def read_properties(self, job_name: str, team_name: str) -> Dict:
        config_parser = ConfigParser()
        config_parser.read(self._file_path)

        # filter properties by prefix for this particular team and data job
        prefix = FileSystemPropertiesServiceClient._prefix(team_name, job_name)
        if config_parser.has_section(prefix):
            return dict(config_parser.items(prefix))
        return {}

    def write_properties(self, job_name: str, team_name: str, properties: Dict) -> Dict:
        log.warning(
            "You are using local FS Properties client. "
            "That means the properties will not be stored using the Control Service."
            "The properties will be read and written to the local file system only."
        )
        config_parser = ConfigParser()
        config_parser.read(self._file_path)

        # filter properties by prefix for this particular team and data job
        prefix = FileSystemPropertiesServiceClient._prefix(team_name, job_name)
        # overwrite section to update its properties
        if config_parser.has_section(prefix):
            config_parser.remove_section(prefix)
        config_parser.add_section(prefix)

        # add section properties
        for k, v in properties.items():
            config_parser.set(prefix, k, v)

        # overwrite file storage with updated values
        with open(self._file_path, "w+") as props_file:
            config_parser.write(props_file)
        return properties

    @staticmethod
    def _prefix(team_name: str, job_name: str):
        return f"{team_name}_{job_name}__"
