# Embed And Ingest Data Job Example

The following Versatile Data Kit example allows you to chunk document data (in certain format).

# Expected input format

```json
[
    {
        "metadata": {
            "title": "Page (or chunk) title",
            "id": "Content page ID",
            "source": "Source URL",
            "deleted": <is the content being deleted in the source>
        },
        "data": "Content Text"
    },
]
```

# Output format

The output format is the same as the input one. The "data" field is the only difference: it now contains a chunk
of a document instead of the whole document.

# Chunking the data

There is a property chunking_strategy which accounts for the type of chunking to use for the documents.
It is set by default to "fixed" which means fixed size chunking with overlap.
The example for the fixed size chunking supports configurable chunking - the CHUNK_SIZE and CHUNK_OVERLAP
are configured in config.py.
They account for the chunk size (tokens) and the chunk overlap between neighbouring chunks of the data.
Another chunking strategy is "wiki" which chunks Wikipedia articles into the different sections.

# Run the example
To run the data job locally:
```bash
vdk run chunker
```
