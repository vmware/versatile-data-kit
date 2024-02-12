# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pathlib

from config import CHUNK_OVERLAP
from config import CHUNK_SIZE
from config import CHUNKS_PKL_FILE_LOCATION
from config import CLEANED_DOCUMENTS_JSON_FILE_LOCATION
from nltk.tokenize import word_tokenize
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def load_documents(json_file_path):
    """
    Loads documents from JSON file.

    :param json_file_path: Path to the JSON file containing documents.
    :return: List of documents.
    """
    with open(json_file_path, encoding="utf-8") as file:
        return json.load(file)


def chunk_fixed_size(documents, chunk_size, chunk_overlap):
    """
    Fixed size chunking - the default strategy for chunking documents.

    :param documents: List of cleaned documents with metadata.
    :param chunk_size: Size of each chunk.
    :param chunk_overlap: Size of overlap between chunks.
    :return: List of chunked documents with their original IDs.
    """
    chunked_documents = []
    for doc in documents:
        tokens = word_tokenize(doc["data"])
        chunks = [
            {"id": doc["metadata"]["id"], "chunk": tokens[i : i + chunk_size]}
            for i in range(0, len(tokens), chunk_size - chunk_overlap)
        ]
        chunked_documents.extend(chunks)
    return chunked_documents


def split_documents_into_chunks(documents, chunk_size, chunk_overlap, strategy):
    """
    Splits documents into chunks based on the specified strategy.

    :param documents: List of documents to be chunked.
    :param chunk_size: Size of each chunk.
    :param chunk_overlap: Size of overlap between chunks.
    :param strategy: The chunking strategy to use.
    :return: List of chunked documents.
    """
    if strategy == "default":
        return chunk_fixed_size(documents, chunk_size, chunk_overlap)
    else:
        log.error(f"Unknown chunking strategy: {strategy}")
        return []


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    data_job_dir = pathlib.Path(job_input.get_job_directory())
    input_json = data_job_dir / CLEANED_DOCUMENTS_JSON_FILE_LOCATION
    output_chunks = data_job_dir / CHUNKS_PKL_FILE_LOCATION
    chunk_size = CHUNK_SIZE
    chunk_overlap = CHUNK_OVERLAP
    chunking_strategy = job_input.get_property("chunking_strategy", "default")

    documents = load_documents(input_json)
    chunked_documents = split_documents_into_chunks(
        documents, chunk_size, chunk_overlap, chunking_strategy
    )
    if chunked_documents:
        log.info(
            f"{len(chunked_documents)} documents chunks created using the {chunking_strategy} chunking strategy."
        )
        with open(output_chunks, "wb") as file:
            import pickle

            pickle.dump(chunked_documents, file)
        log.info(f"Chunks saved to {output_chunks}")
