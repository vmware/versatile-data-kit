# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Any
from typing import List
from typing import Optional
from typing import Union


class IStorage:
    def store(self, name: str, content: Union[str, bytes, Any]) -> None:
        """
        Stores the given content under the specified name. If the content is not a string or bytes,
        the method tries to serialize it based on the content_type (if provided) or infers the type.

        :param name: The unique name to store the content under.
        :param content: The content to store. Can be of type str, bytes, or any serializable type.
        """
        pass

    def retrieve(self, name: str) -> Optional[Union[str, bytes, Any]]:
        """
        Retrieves the content stored under the specified name. The method attempts to deserialize
        the content to its original type if possible.

        :param name: The name of the content to retrieve.
        :return: The retrieved content, which can be of type str, bytes, or any deserialized Python object.
                 Returns None if the content does not exist.
        """
        pass

    def list_contents(self) -> List[str]:
        """
        Lists the names of all stored contents.

        :return: A list of names representing the stored contents.
        """
        pass

    def remove(self, name: str) -> bool:
        """
        Removes the content stored under the specified name.

        :param name: The name of the content to remove.
        :return: True if the content was successfully removed, False otherwise.
        """
        pass
