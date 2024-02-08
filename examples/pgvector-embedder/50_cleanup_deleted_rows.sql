-- TODO (missing vdk feature): this may not be necessary if our Ingestion framework supports deletion

-- Step 1: Delete from metadata table where deleted is true
DELETE FROM public.{destination_metadata_table}
WHERE deleted = TRUE;

-- Step 2: Delete from embeddings table where id not present in metadata table
DELETE FROM public.{destination_embeddings_table}
WHERE id NOT IN (
    SELECT id FROM public.{destination_metadata_table}
);
