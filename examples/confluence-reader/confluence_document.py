
class ConfluenceDocument:
    def __init__(self, metadata, page_content, deleted=False):
        """
        Initializes a ConfluenceDocument instance.

        :param metadata: A dictionary containing metadata about the Confluence document.
                         Expected to contain 'title', 'id', and 'source'.
        :param page_content: A string representing the content of the Confluence page.
        :param deleted: A boolean indicating whether the document is considered deleted.
        """
        self.validate_metadata(metadata)
        self.metadata = metadata
        self.page_content = page_content
        self.deleted = deleted

    def serialize(self):
        """
        Serializes the ConfluenceDocument instance into a dictionary.
        """
        return {
            'metadata': self.metadata,
            'page_content': self.page_content,
            'deleted': self.deleted
        }

    @staticmethod
    def validate_metadata(metadata):
        """
        Validates the metadata dictionary to ensure it contains required keys.

        :param metadata: A dictionary containing metadata about the Confluence document.
        :raises ValueError: If metadata does not contain the required keys.
        """
        required_keys = {'title', 'id', 'source'}
        if not required_keys.issubset(metadata):
            missing_keys = required_keys - metadata.keys()
            raise ValueError(f"Metadata is missing required keys: {missing_keys}")

