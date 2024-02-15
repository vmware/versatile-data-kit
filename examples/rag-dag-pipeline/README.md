This jobs contains a ETL (Extract, Load, Transform) pipelines designed for processing data from Confluence and embedding it using pgvector

The jobs are orchestrated using the vdk-dag plugin to run in a defined sequence.

# Job structure

Here are the two main jobs:

- Extracts raw data from Confluence and loads it into a specified location (table, file, etc.).
- pgvector-embedder: Transforms the extracted data by embedding it using pgvector and stores the metadata and embeddings in specified tables (vdk_confluence_metadata and vdk_confluence_embeddings).

TODO (missing vdk feature): as the idea is for this to be used as a template, we need to allow somehow VDK to handle automatically jobs specified in the DAG
Currently a the job specified (e.g confluence-reader) must be deployed and deployed VDK jobs can only run one execution at a time.
What can we do to solve that?

A) Create a separate deployment automatically
B) Run the job with the arguments provided as a separate job instance
    - what about job properties - maybe it should inhert the parent job properties ? Or ignore them and only accept arguments?
C) ...

TODO (missing vdk feature): how do I pick between different jobs to compose them?
