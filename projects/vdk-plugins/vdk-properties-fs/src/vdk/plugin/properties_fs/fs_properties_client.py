# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
from typing import Dict
from typing import Optional

from vdk.api.plugin.plugin_input import IPropertiesServiceClient

log = logging.getLogger(__name__)


class FileSystemPropertiesServiceClient(IPropertiesServiceClient):
    """
    Implementation of IProperties that are kept on local FS only. Stateless.
    A single JSON file store, supporting multiple teams and data jobs properties,
    via nesting the key-values under a dedicated team and job name key to deduplicate.
    """

    def __init__(self, directory: str, filename: str):
        self._file_path = os.path.join(directory, filename)

    def read_properties(self, job_name: str, team_name: str) -> Dict:
        if os.path.isfile(self._file_path) and os.stat(self._file_path).st_size != 0:
            props: Dict
            with open(self._file_path) as props_file:
                props = json.load(props_file)

            # filter properties by prefix for this particular team and data job
            prefix = FileSystemPropertiesServiceClient._prefix(team_name, job_name)
            if props.keys().__contains__(prefix):
                return props.get(prefix)
        return {}

    def write_properties(self, job_name: str, team_name: str, properties: Dict) -> Dict:
        log.warning(
            "You are using local FS Properties client. "
            "That means the properties will not be stored using the Control Service, yet FS storage is stateful and "
            "all properties data will survive VDK process restarts."
            "The properties will be read and written to the local file system only."
        )
        props: Optional[Dict] = None

        # init storage file
        if not os.path.isfile(self._file_path) or os.stat(self._file_path).st_size == 0:
            with open(self._file_path, "w+") as props_file:
                props = {}
                json.dump(props, props_file)

        with open(self._file_path, "r+") as props_file:
            props = json.load(props_file) if props is None else props

            # filter properties by prefix for this particular team and data job
            prefix = FileSystemPropertiesServiceClient._prefix(team_name, job_name)
            # overwrite properties
            props_file.seek(0)
            props.update({prefix: properties})
            props_file.truncate()
            # store
            json.dump(props, props_file)
        return properties

    @staticmethod
    def _prefix(team_name: str, job_name: str):
        return f"{team_name}_{job_name}__"
