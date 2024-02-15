# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0

import csv
import logging
import pathlib
import re

import nltk
from config import DOCUMENTS_CSV_FILE_LOCATION
from config import EMBEDDINGS_PKL_FILE_LOCATION
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def clean_text(text):
    """
    Prepares text for NLP tasks (embedding and RAG) by standardizing its form. It focuses on retaining
    meaningful words and achieving consistency in their representation. This involves
    converting to lowercase (uniformity), removing punctuation and stopwords
    (focusing on relevant words), and lemmatization (reducing words to their base form).
    Such preprocessing is crucial for effective NLP analysis.

    :param text: A string containing the text to be processed.
    :return: The processed text as a string.
    """
    text = text.lower()
    # remove punctuation and special characters
    text = re.sub(r"[^\w\s]", "", text)
    # remove stopwords and lemmatize
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    text = " ".join(
        [lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words]
    )
    return text


def load_and_clean_documents(filename):
    cleaned_documents = []
    with open(filename, encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if row:
                cleaned_text = clean_text(row[0])
                cleaned_documents.append([cleaned_text])
    return cleaned_documents


def save_cleaned_documents(cleaned_documents, output_file):
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(cleaned_documents)


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
    return embeddings


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    input_csv = DOCUMENTS_CSV_FILE_LOCATION
    # output_cleaned_csv = 'documents_cleaned.csv'
    data_job_dir = pathlib.Path(job_input.get_job_directory())
    output_embeddings = data_job_dir / EMBEDDINGS_PKL_FILE_LOCATION

    # create a temporary (until the end of the job execution) dir with
    # write permissions to store the relevant nltk dependencies
    temp_dir = job_input.get_temporary_write_directory()
    nltk_data_path = temp_dir / "nltk_data"
    nltk_data_path.mkdir(exist_ok=True)
    nltk.data.path.append(str(nltk_data_path))

    nltk.download("stopwords", download_dir=str(nltk_data_path))
    nltk.download("wordnet", download_dir=str(nltk_data_path))

    cleaned_documents = load_and_clean_documents(input_csv)
    if cleaned_documents:
        log.info(
            f"{len(cleaned_documents)} documents loaded and cleaned for embedding."
        )
        # save_cleaned_documents(cleaned_documents, output_cleaned_csv)
        # log.info(f"Cleaned documents saved to {output_cleaned_csv}")
        embeddings = embed_documents_in_batches(cleaned_documents)
        with open(output_embeddings, "wb") as file:
            import pickle

            pickle.dump(embeddings, file)
        log.info(f"Embeddings saved to {output_embeddings}")
