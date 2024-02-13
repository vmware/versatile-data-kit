# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0


class ConfluenceDocument:
    def __init__(self, metadata, data, deleted=False):
        """
        Initializes a ConfluenceDocument instance.

        :param metadata: A dictionary containing metadata about the Confluence document.
                         Expected to contain 'title', 'id', and 'source'.
                         'deleted' key will be added to indicate if the document is considered deleted.
        :param data: A string representing the content of the Confluence page.
        """
        self.validate_metadata(metadata)
        metadata["deleted"] = deleted
        self.metadata = metadata
        self.data = data

    def serialize(self):
        """
        Serializes the ConfluenceDocument instance into a dictionary.
        """
        return {"metadata": self.metadata, "data": self.data}

    @staticmethod
    def validate_metadata(metadata):
        """
        Validates the metadata dictionary to ensure it contains required keys plus checks for 'deleted'.

        :param metadata: A dictionary containing metadata about the Confluence document.
        :raises ValueError: If metadata does not contain the required keys ('title', 'id', 'source').
        """
        required_keys = {"title", "id", "source"}
        if not required_keys.issubset(metadata):
            missing_keys = required_keys - metadata.keys()
            raise ValueError(f"Metadata is missing required keys: {missing_keys}")
