# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
import pickle

from config import CHUNKS_PKL_FILE_LOCATION
from config import EMBEDDINGS_PKL_FILE_LOCATION
from sentence_transformers import SentenceTransformer
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def load_document_chunks(input_chunks_path):
    """
    Loads document chunks from Pickle file.

    :param input_chunks_path: Path to the Pickle file containing document chunks.
    :return: List of document chunks.
    """
    with open(input_chunks_path, "rb") as file:
        return pickle.load(file)


def embed_documents(documents):
    """
    Embeds the chunks of each document.

    :param documents: Documents split into chunks to be embedded.
    :return: List of embeddings for each chunk of each document.
    """
    # the model card: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
    model = SentenceTransformer("all-mpnet-base-v2")
    embeddings = []
    for doc_chunks in documents:
        chunk_embeddings = []
        for chunk in doc_chunks:
            # join the list of tokens in each chunk
            chunk = " ".join(chunk)
            chunk_embeddings.append(model.encode(chunk, show_progress_bar=True))
        embeddings.append(chunk_embeddings)

    return embeddings


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    data_job_dir = pathlib.Path(job_input.get_job_directory())
    input_chunks = data_job_dir / CHUNKS_PKL_FILE_LOCATION
    output_embeddings = data_job_dir / EMBEDDINGS_PKL_FILE_LOCATION

    chunks = load_document_chunks(input_chunks)
    embeddings = embed_documents(chunks)
    if embeddings:
        log.info(f"{len(embeddings)} embeddings created.")
        with open(output_embeddings, "wb") as file:
            pickle.dump(embeddings, file)
        log.info(f"Embeddings saved to {output_embeddings}")
