# Fetch And Embed Data Job Example

The following Versatile Data Kit example allows you to fetch the data from public Confluence space and embed it.

# Fetch Confluence Data
The data is fetched in [10_fetch_confluence_space.py](./10_fetch_confluence_space.py) using the
[LangChain's ConfluenceLoader](https://python.langchain.com/docs/integrations/document_loaders/confluence).

# Create embeddings for the data
The fetched data from the previous step is read, cleaned and embedded using the
[all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) HuggingFace SentenceTransformer Embedding model:

# Run the example
To run the data job locally:
```bash
vdk run fetch-embed-job-example
```

To open the output embeddings pickle file, use:

```python
import pandas as pd

obj = pd.read_pickle(r'embeddings.pkl')
```
