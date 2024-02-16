# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from typing import Any
from typing import List
from typing import Optional
from typing import Union

from storage import IStorage


class FileStorage(IStorage):
    def __init__(self, base_path: str):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def _get_file_path(self, name: str) -> str:
        return os.path.join(self.base_path, name)

    def store(
        self,
        name: str,
        content: Union[str, bytes, Any],
        content_type: Optional[str] = None,
    ) -> None:
        file_path = self._get_file_path(name)
        with open(file_path, "w") as file:
            if isinstance(content, (str, bytes)):
                # Directly save strings and bytes
                file.write(content if isinstance(content, str) else content.decode())
            else:
                # Assume JSON serializable for other types
                json.dump(content, file)

    def retrieve(self, name: str) -> Optional[Union[str, bytes, Any]]:
        file_path = self._get_file_path(name)
        if not os.path.exists(file_path):
            return None
        with open(file_path) as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                # Content was not JSON, return as string
                file.seek(0)
                return file.read()

    def list_contents(self) -> List[str]:
        return os.listdir(self.base_path)

    def remove(self, name: str) -> bool:
        file_path = self._get_file_path(name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
