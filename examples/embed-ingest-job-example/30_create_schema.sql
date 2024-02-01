DROP TABLE IF EXISTS public.vdk_confluence_doc_embeddings_example CASCADE;
DROP TABLE IF EXISTS public.vdk_confluence_doc_metadata_example CASCADE;


CREATE TABLE IF NOT EXISTS public.vdk_confluence_doc_embeddings_example
(
    id SERIAL PRIMARY KEY,
    embedding public.vector
);

CREATE TABLE IF NOT EXISTS public.vdk_confluence_doc_metadata_example
(
    id INTEGER PRIMARY KEY,
    title TEXT,
    source TEXT,
    content TEXT,
    CONSTRAINT fk_metadata_embeddings FOREIGN KEY (id) REFERENCES public.vdk_confluence_doc_embeddings_example(id)
);
