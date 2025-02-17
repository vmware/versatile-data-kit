# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
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
    return text


def get_question_embedding(question):
    model = SentenceTransformer("all-mpnet-base-v2")
    embedding = model.encode(clean_text(question))

    return embedding
