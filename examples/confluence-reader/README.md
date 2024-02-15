# Confluence Data Retrieval Example

In this data job example, we demonstrate how to efficiently retrieve and manage data from a Confluence space using the Confluence Data Retrieval Class. This class is a versatile utility that simplifies the process of fetching, tracking updates, and flagging deleted pages in a Confluence space. The resulting data is stored in a JSON file for further analysis.

## Confluence Data Retrieval Class

The `ConfluenceDataSource` class is the heart of this data job. It provides a set of methods for interacting with Confluence data:

- `fetch_updated_pages_in_confluence_space()`: Fetches updated pages in the Confluence space based on the last modification date.
- `fetch_all_pages_in_confluence_space()`: Retrieves all pages in the Confluence space.
- `flag_deleted_pages()`: Flags deleted pages based on the current Confluence data.
- `update_saved_documents()`: Updates the saved documents in the JSON file with the latest data.

These methods make use of the last_modification.txt file to determine the last modification date and track changes in the Confluence space, allowing for efficient data retrieval and management.

## JSON Data Format

The resulting JSON data (confluence_data.json) is generated using the `ConfluenceDocument` class (see confluence_document.py).
It follows this structured format:

```json
[
    {
        "metadata": {
            "title": "Page Title",
            "id": "Page ID",
            "source": "Source URL",
            "deleted": false
        },
        "data": "Page Content Text"
    },
    {
        "metadata": {
            "title": "Another Page Title",
            "id": "Another Page ID",
            "source": "Another Source URL",
            "deleted": true
        },
        "data": "Another Page Content Text"
    }
]

```
