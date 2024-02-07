# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pathlib
import re

from config import CHUNK_OVERLAP
from config import CHUNK_SIZE
from config import DOCUMENTS_JSON_FILE_LOCATION
from config import EMBEDDINGS_PKL_FILE_LOCATION
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def clean_text(text):
    """
    Prepares text for NLP tasks (embedding and RAG) by standardizing its form. This involves
    converting to lowercase (uniformity) and removing punctuation and special characters.

    :param text: A string containing the text to be processed.
    :return: The processed text as a string.
    """
    text = text.lower()
    # remove punctuation and special characters
    text = re.sub(r"[^\w\s]", "", text)
    return text


def load_and_clean_documents(json_file_path):
    """
    Loads the documents and cleans them.

    :param json_file_path: Path to the JSON file containing the documents.
    :return: List of cleaned documents.
    """
    cleaned_documents = []
    with open(json_file_path, encoding="utf-8") as file:
        documents = json.load(file)

    for doc in documents:
        if "data" in doc:
            cleaned_text = clean_text(doc["data"])
            cleaned_documents.append([cleaned_text])

    print(len(cleaned_documents))
    return cleaned_documents


def split_documents_into_chunks(
    documents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
):
    """
    Splits documents into smaller chunks with specified overlap.

    :param documents: List of documents to be chunked.
    :param chunk_size: Size of each chunk.
    :param chunk_overlap: Size of overlap between chunks.
    :return: List of chunked documents.
    """
    chunked_documents = []
    for doc in documents:
        tokens = word_tokenize(doc[0])
        chunks = [
            tokens[i : i + chunk_size]
            for i in range(0, len(tokens), chunk_size - chunk_overlap)
        ]
        chunked_documents.append(chunks)
    return chunked_documents


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
    input_json = data_job_dir / DOCUMENTS_JSON_FILE_LOCATION
    output_embeddings = data_job_dir / EMBEDDINGS_PKL_FILE_LOCATION

    cleaned_documents = load_and_clean_documents(input_json)
    if cleaned_documents:
        log.info(
            f"{len(cleaned_documents)} documents loaded and cleaned for embedding."
        )
        chunked_documents = split_documents_into_chunks(cleaned_documents)
        embeddings = embed_documents(chunked_documents)
        with open(output_embeddings, "wb") as file:
            import pickle

            pickle.dump(embeddings, file)
        log.info(f"Embeddings saved to {output_embeddings}")
