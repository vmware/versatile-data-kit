# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer

# This file contains all the reused code from vdk example jobs


def clean_text(text):
    """
    TODO: Copied from the embed-ingest-job-example. Needs to be replaced by a more robust approach, something
    off the shelf ideally.
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


def setup_nltk(temp_dir):
    """
    Set up NLTK by creating a temporary directory for NLTK data and downloading required resources.
    """
    from pathlib import Path

    nltk_data_path = Path(temp_dir) / "nltk_data"

    nltk_data_path.mkdir(exist_ok=True)
    nltk.data.path.append(str(nltk_data_path))
    if os.path.isdir(nltk_data_path):
        return

    nltk.download("stopwords", download_dir=str(nltk_data_path))
    nltk.download("wordnet", download_dir=str(nltk_data_path))


def get_question_embedding(question):
    model = SentenceTransformer("all-mpnet-base-v2")
    embedding = model.encode(clean_text(question))

    return embedding
