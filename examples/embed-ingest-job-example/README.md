# Embed And Ingest Data Job Example

The following Versatile Data Kit example allows you to embed documenta data and metadata (in certain format)
and ingest it into Postgres instance with pgvector.

# Expected input format

```python
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
```

# Create embeddings for the data
The fetched data from the previous step is read, cleaned and embedded using the
[all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) HuggingFace SentenceTransformer Embedding model.

To open the output embeddings pickle file, use:

```python
import pandas as pd

obj = pd.read_pickle(r'embeddings_example.pkl')
```

# Ingest into Postgres

In order to connect to the database, we use [vdk-postgres](https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-postgres).
You should set the relevant postgres parameters for your instance in the config.ini file.

# Run the example
To run the data job locally:
```bash
vdk run embed-ingest-job-example
```
