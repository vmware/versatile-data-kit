# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging

from config import get_value
from sentence_transformers import SentenceTransformer
from vdk.api.job_input import IJobInput
from vdk.plugin.storage.database_storage import DatabaseStorage

log = logging.getLogger(__name__)


def embed_documents_in_batches(documents):
    # the model card: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
    model = SentenceTransformer("all-mpnet-base-v2")
    total = len(documents)
    log.info(f"total: {total}")
    embeddings = []
    for start_index in range(0, total):
        # the resources are not enough to batch 2 documents at a time, so the batch = 1 doc
        batch = [documents[start_index]]
        log.info(f"BATCH: {len(batch)}.")
        embeddings.extend(model.encode(batch, show_progress_bar=True))

    print(len(embeddings))
    return embeddings


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    output_embeddings = get_value(job_input, "output_embeddings")
    storage = DatabaseStorage(get_value(job_input, "storage_connection_string"))
    storage_name = get_value(job_input, "storage_name", "confluence_data")

    documents = storage.retrieve(storage_name)
    if documents:
        log.info(f"{len(documents)} chunks loaded and cleaned for embedding.")
        embeddings = embed_documents_in_batches(documents)
        with open(output_embeddings, "wb") as file:
            import pickle

            pickle.dump(embeddings, file)
        log.info(f"Embeddings saved to {output_embeddings}")
