# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pickle

import numpy as np
from config import get_value
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Starting job step {__name__}")

    input_embeddings_path = get_value(job_input, "output_embeddings")
    input_documents_path = get_value(job_input, "data_file")

    with open(input_embeddings_path, "rb") as file:
        embeddings = pickle.load(file)
    with open(input_documents_path) as file:
        documents = json.load(file)

    print(len(documents), len(embeddings))

    # TODO: our postgres plugin doesn't support updates (upserts) so updating with same ID fails.

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
            destination_table=get_value(job_input, "destination_embeddings_table"),
        )

    for document in documents:
        metadata_payload = {
            "id": document["metadata"]["id"],
            "title": document["metadata"]["title"],
            "data": document["data"],
            "source": document["metadata"]["source"],
            "deleted": document["metadata"]["deleted"],
        }
        job_input.send_object_for_ingestion(
            payload=metadata_payload,
            destination_table=get_value(job_input, "destination_metadata_table"),
        )
