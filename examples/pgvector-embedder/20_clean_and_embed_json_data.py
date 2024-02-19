# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import re

from common.database_storage import DatabaseStorage
from config import get_value
from sentence_transformers import SentenceTransformer
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def clean_text(text):
    """
    Prepares text for NLP tasks (embedding and RAG) by standardizing its form.
    :param text: A string containing the text to be processed.
    :return: The processed text as a string.
    """
    return text


def load_and_clean_documents(content):
    cleaned_documents = []
    documents = json.loads(content)

    for doc in documents:
        if "data" in doc:
            cleaned_text = clean_text(doc["data"])
            cleaned_documents.append([cleaned_text])

    print(len(cleaned_documents))
    return cleaned_documents


def embed_documents_in_batches(documents):
    # the model card: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
    model = SentenceTransformer("all-mpnet-base-v2")
    total = len(documents)
    log.info(f"total: {total}")
    embeddings = []
    for start_index in range(0, total):
        # the resources are not enough to batch 2 documents at a time, so the batch = 1 doc
        batch = documents[start_index]
        log.info(f"BATCH: {len(batch)}.")
        embeddings.extend(model.encode(batch, show_progress_bar=True))

    print(len(embeddings))
    return embeddings


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    output_embeddings = get_value(job_input, "output_embeddings")

    storage = DatabaseStorage(get_value(job_input, "storage_connection_string"))
    storage_name = get_value(job_input, "storage_name", "confluence_data")

    cleaned_documents = load_and_clean_documents(storage.retrieve(storage_name))
    if cleaned_documents:
        log.info(
            f"{len(cleaned_documents)} documents loaded and cleaned for embedding."
        )
        embeddings = embed_documents_in_batches(cleaned_documents)
        with open(output_embeddings, "wb") as file:
            import pickle

            pickle.dump(embeddings, file)
        log.info(f"Embeddings saved to {output_embeddings}")
