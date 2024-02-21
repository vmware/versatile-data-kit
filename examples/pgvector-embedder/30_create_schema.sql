--TODO (missing vdk feature): we need to drop the tables as postgres pluigin doesn't support upserts (updates)

DROP TABLE IF EXISTS public.{destination_metadata_table} CASCADE;
DROP TABLE IF EXISTS public.{destination_embeddings_table} CASCADE;

-- TODO (missing vdk feature): we need to create the tables as the postgres plugin doesn't support automatic schema inference
CREATE TABLE IF NOT EXISTS public.{destination_embeddings_table}
(
    id TEXT PRIMARY KEY,
    embedding public.vector
);

CREATE TABLE IF NOT EXISTS public.{destination_metadata_table}
(
    id TEXT PRIMARY KEY,
    title TEXT,
    source TEXT,
    data TEXT,
    deleted BOOLEAN
);

CREATE TABLE IF NOT EXISTS public.{destination_embeddings_table}
(
    id VARCHAR PRIMARY KEY,
    embedding public.vector,
    CONSTRAINT fk_embeddings_metadata FOREIGN KEY (id) REFERENCES public.{destination_metadata_table}(id)
);
