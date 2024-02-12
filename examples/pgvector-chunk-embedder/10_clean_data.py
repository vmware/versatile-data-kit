# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pathlib
import re

from config import CLEANED_DOCUMENTS_JSON_FILE_LOCATION
from config import DOCUMENTS_JSON_FILE_LOCATION
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
            cleaned_documents.append(
                {"metadata": doc["metadata"], "data": cleaned_text}
            )

    print(len(cleaned_documents))
    return cleaned_documents


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    data_job_dir = pathlib.Path(job_input.get_job_directory())
    input_json = data_job_dir / DOCUMENTS_JSON_FILE_LOCATION
    output_json = data_job_dir / CLEANED_DOCUMENTS_JSON_FILE_LOCATION

    cleaned_documents = load_and_clean_documents(input_json)
    if cleaned_documents:
        log.info(
            f"{len(cleaned_documents)} documents loaded and cleaned for embedding."
        )
        with open(output_json, "w", encoding="utf-8") as output_file:
            json.dump(cleaned_documents, output_file, indent=4)
        log.info(f"Cleaned documents saved to {output_json}")
