# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pathlib
import pickle

import numpy as np
from config import DOCUMENTS_JSON_FILE_LOCATION
from config import EMBEDDINGS_PKL_FILE_LOCATION
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    data_job_dir = pathlib.Path(job_input.get_job_directory())
    input_embeddings_path = data_job_dir / EMBEDDINGS_PKL_FILE_LOCATION
    input_documents_path = data_job_dir / DOCUMENTS_JSON_FILE_LOCATION

    with open(input_embeddings_path, "rb") as file:
        embeddings = pickle.load(file)
    with open(input_documents_path) as file:
        documents = json.load(file)

    print(len(documents), len(embeddings))

    for i, embedding in enumerate(embeddings):
        embedding_list = (
            embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        )
        embedding_payload = {
            "id": documents[i]["metadata"]["id"],
            "embedding": embedding_list,
        }
        job_input.send_object_for_ingestion(
            payload=embedding_payload,
            destination_table="vdk_confluence_doc_embeddings_example",
        )

    for document in documents:
        metadata_payload = {
            "id": document["metadata"]["id"],
            "title": document["metadata"]["title"],
            "content": document["page_content"],
            "source": document["metadata"]["source"],
        }
        job_input.send_object_for_ingestion(
            payload=metadata_payload,
            destination_table="vdk_confluence_doc_metadata_example",
        )
